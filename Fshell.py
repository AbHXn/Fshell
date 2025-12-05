from Headers.CmdHandlers import ScriptHandler, DoubleCmdHandler, SingleCmdHandler
from termcolor import cprint, colored
from Headers.CmdConstants import *
from datetime import date
import sys
import platform
import os

# convert raw inputs to tokens
class RawCmdParser:
	def __init__(self, cmd_string):
		self.cmd_string = cmd_string

	def getUntil(self, start_index, c_char):
		cur_data  = c_char

		while start_index < len( self.cmd_string ):

			if self.cmd_string[ start_index ] == c_char:
				cur_data += c_char
				return start_index, cur_data.strip()
	
			cur_data  += self.cmd_string[ start_index ]
			start_index += 1
		
		return None

	def getList(self, start_index ):
		list_data = []
		cur_data  = ''

		while start_index < len( self.cmd_string ):
			if self.cmd_string[ start_index ] == LIST_CLOSE:
				if len( cur_data ) > 0:
					list_data.append( cur_data )
				return start_index, list_data

			if self.cmd_string[ start_index ].isspace():
				if len( cur_data ) > 0:
					list_data.append( cur_data )
					cur_data = ''
			
			elif self.cmd_string[ start_index ] == EXPR_OPEN:
				cmd_length, push_node = self.getExpr( self.cmd_string, start_index ) or [0, None]
				if push_node:
					list_data.append( push_node )
					start_index = cmd_length

			elif self.cmd_string[ start_index ] == APPO:
				cmd_length, push_node = self.getUntil( self.cmd_string, start_index + 1, APPO ) or [0, None]
				if push_node:
					list_data.append( push_node )
					start_index = cmd_length

			else: cur_data += self.cmd_string[ start_index ]
			start_index += 1

		return None

	def getExpr(self, start_index ):
		cur_index 	= start_index
		cur_data  	= ''
		expr_opened = 0

		while cur_index < len( self.cmd_string ):
			cur_data  += self.cmd_string[ cur_index ]
			
			if self.cmd_string[ cur_index ] == EXPR_CLOSE:
				expr_opened -= 1
				if not expr_opened:
					return cur_index, cur_data

			if self.cmd_string[ cur_index ] == EXPR_OPEN:
				expr_opened += 1

			cur_index += 1

		return None

	def getRawCmdChain( self ):
		self.cmd_string = self.cmd_string.strip() + ' '
		cur_index, end_index = 0, len( self.cmd_string )

		raw_cmd_chain = []

		while cur_index < end_index:
			c_char = self.cmd_string[ cur_index ]
			data = None

			if c_char.isspace():
				cur_index += 1
				continue

			if c_char == LIST_OPEN:
				data = self.getList( cur_index + 1 )

			elif c_char == EXPR_OPEN:
				data = self.getExpr( cur_index )

			elif c_char in S_CMDS_A or c_char in S_CMDS_B:
				raw_cmd_chain.append( c_char )

			elif c_char == APPO:
				data = self.getUntil( cur_index + 1, APPO )
	
			else: data = self.getUntil( cur_index , ' ' )

			cmd_length, push_node = data if data else [0, None]

			if push_node is not None:
				if isinstance( push_node, str ) and push_node.endswith(LIST_CONTENTS):
					raw_cmd_chain.append( push_node[:-1] )
					raw_cmd_chain.append( push_node[-1] )
				else:
					raw_cmd_chain.append( push_node )
					push_node = None
				cur_index = cmd_length

			cur_index += 1
		return raw_cmd_chain

#convert tokens to CmdHandler and execute
class CmdExecuter( RawCmdParser ):
	def __init__(self, rawStringCmd ):
		super().__init__( rawStringCmd )
		self.rawCmdToHandler()
		self.trace_folder = BASE_DIR

	def execute_commands( self ):
		if self.cmdHandler is None:
			sys.stderr.write("Failed to execute command\n")
			return False

		for cmdHnd in self.cmdHandler:
			if not cmdHnd.execute_command( self.trace_folder ):
				return False 
			if cmdHnd.optr == CHDIR:
				self.trace_folder = BASE_DIR

		return True

	def rawCmdToHandler( self ):
		cmdList = self.getRawCmdChain()
		if cmdList is None:
			self.cmdHandler = None
			return

		tempStack 	= []
		CmdHandler  = []
		optr 	  = None
		double    = False

		for cmd in cmdList:
			if isinstance( cmd, list ):
				tempStack.append( cmd )
			else:
				cmd = cmd.strip()
				if cmd.startswith( EXPR_OPEN ):
					tempStack.append( ScriptHandler( cmd ) )

				elif cmd in D_CMDS:
					optr   = cmd
					double = True
					continue

				elif cmd in S_CMDS_B:
					optr = cmd
					continue

				elif cmd not in S_CMDS_A: 
					tempStack.append( cmd )

			if optr is not None or cmd in S_CMDS_A:
				optr = optr or cmd

				if tempStack == []:
					tempStack.append( BASE_DIR )
				right = tempStack.pop()

				if not double:
					nCmdHnd = SingleCmdHandler( right, optr )
					CmdHandler.append( nCmdHnd )
					optr = None
					continue

				if double and tempStack == []:
					tempStack.append( BASE_DIR )

				left = tempStack.pop()
				nCmdHnd = DoubleCmdHandler( left, right, optr ) 
				CmdHandler.append( nCmdHnd )
				optr   = None
				double = False

		self.cmdHandler = CmdHandler

def input_cmd( ):
	run_input = True
	full_cmd = ''

	opened = 0
	while run_input:
		if not opened:
			cmd = input(colored(f"{date.today()}::$ ", "cyan"))
		else: cmd = input(colored("::$ ", "cyan"))
		opened += cmd.count( LIST_OPEN ) + cmd.count( EXPR_OPEN )
		opened -= cmd.count( LIST_CLOSE ) + cmd.count( EXPR_CLOSE ) 

		full_cmd += cmd
		if opened > 0:
			continue
		elif opened < 0:
			raise ValueError("Invalid Command")
		return full_cmd


if __name__ == "__main__":
	if platform.system() == "Windows":
		os.system("cls")
	else:
		os.system("clear")

	while True:
		try:
			cmd = input_cmd( )
			cmd = cmd.strip()
			cmd_executer = CmdExecuter( cmd )
			cmd_executer.execute_commands() 
		except Exception as error:
			cprint(f"ErRrRoR {error}", "red")
