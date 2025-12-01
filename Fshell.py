from datetime import date
from termcolor import cprint, colored
import subprocess
import sys
import platform
import os
import shutil

REMOVE      	= '-'
CREATE      	= '+'
COPY        	= '+='
CUT         	= '-='
CHDIR       	= '*'
INPUT       	= '#'
EXPR_OPEN   	= '{'
EXPR_CLOSE  	= '}'
LIST_OPEN   	= '['
LIST_CLOSE  	= ']'
LIST_CONTENTS 	= '!'
APPO			= '"'

# didn't implemented
RE_APPEND 		= "=="
RE_ASSIGN		= "="

D_CMDS   = ( REMOVE, CREATE, COPY, CUT, RE_ASSIGN, RE_APPEND )
S_CMDS_A = ( LIST_CONTENTS, )
S_CMDS_B = ( INPUT, CHDIR )

BASE_DIR = '.'

class ExecUtils:

	@staticmethod
	def create_file(base, name):
		try:
			if name == "":  return False
			path = os.path.join(base, name)
			if name.endswith('/') or name.endswith(os.sep):
				os.makedirs(path, exist_ok=True)
			else:
				os.makedirs(os.path.dirname(path), exist_ok=True)
				if not os.path.exists(path):
					with open(path, "w") as file:
						pass
			return True
		except Exception as e:
			cprint(f"File Creation Failed: {e}", "red")
			return False

	@staticmethod
	def remove_file(path):
		try:
			if os.path.isdir(path):
				shutil.rmtree(path)
			elif os.path.exists(path):
				os.remove(path)
			return True
		except Exception as e:
			cprint(f"File Remove Error: {e}", "red")
			return False

	@staticmethod
	def copy_file(src, dst):
		try:
			print(src, dst)
			if os.path.exists(dst) and os.path.isdir(dst):
				if os.path.isdir(src):
					print("here")
					shutil.copytree(src, os.path.join( dst,
							os.path.basename(src)), dirs_exist_ok=True)
				else:
					os.makedirs(dst, exist_ok=True)
					shutil.copy2(src, os.path.join(dst, os.path.basename(src)))
			else: 
				with open(dst, "w", encoding='utf-8') as file_w:
					with open(src, "r", encoding="utf-8") as file_r:
						file_w.write(file_r.read())
			return True
		except Exception as e:
			cprint( f"File Copy Error: {e}", "red" )
			return False

	@staticmethod
	def move_file(src, dst):
		try:
			if os.path.exists(src) and os.path.exists(dst):
				shutil.move(src, dst)
			else: os.rename(src, dst)
			return True
		except Exception:
			cprint( f"File Move Error: {e}" , "red")
			return False

	@staticmethod
	def list_contents(folders):
		if not isinstance(folders, list):
			folders = [('.', folders)]
		try:
			for parent, child in folders:
				folder = os.path.join(parent, child) 
				cprint(f"{child}:", "green")
				if os.path.exists(folder) and os.path.isfile(folder):
					with open(folder, "r", encoding="utf-8") as txt_file:
						print(txt_file.read())
					return
				with os.scandir(folder) as d_files:
					for file_ in d_files:
						name = file_.name
						name = colored(name, 'blue') if file_.is_dir() else name
						print(f"{name}", end="  ")
					print()
		except Exception as error:
			cprint( f"Listing Error: {e}", "red" )

	@staticmethod
	def input_file(file_name):
		print(f"Enter text for {file_name} (Ctrl+C to save):")
		try:
			with open(file_name, "w", encoding='utf-8') as w_file:
				while True:
					line = input()
					w_file.write(line + '\n')
		except KeyboardInterrupt:
			cprint( "File Saved", "green" )

class ScriptHandler:
	def __init__(self, script):
		self.script = script

	def execute(self, folder):
		try:
			dir_files = os.listdir(folder)
			
			self.script = self.script[1:-1].replace( '*', str(dir_files) )
			results = eval( self.script )
			cprint(f"\tSCRIPT RESULT\n{results}", "green")
			print()
			return [line.strip() for line in results if line.strip()]
		except Exception as e:
			cprint(f"Script execution failed: {e}", "red")
			return []

class DoubleCmdHandler:
	def __init__(self, left, right, optr):
		self.left  = left
		self.right = right
		self.optr = optr

	def execute_command( self, currentFolder ):
		leftFiles 	 = self._full_path_data( self.left, currentFolder )
		righFIles    = self._full_path_data( self.right, currentFolder )
		finalContent = self.join_contents( leftFiles, righFIles ) 

		if finalContent == []: return False

		for source, dest in finalContent:
			source = os.path.join( currentFolder, source )
			if self.optr == CREATE:
				if os.path.exists(source):
					ExecUtils.create_file(source, dest)
				else: print(f"{ source } not exists.")

			elif self.optr == REMOVE:
				full_file = os.path.join( source, dest )
				if os.path.exists(full_file):
					ExecUtils.remove_file(full_file)
				else: print(f"{dest} not found.")			

			elif self.optr in (COPY, CUT):
				if os.path.exists( source ):
					if self.optr == COPY: 
						ExecUtils.copy_file(source, dest)
					else: ExecUtils.move_file(source, dest)
				else: print(f"Source {dest} not found.")
		return True

	def _full_path_data( self , CmdHandler, folder ):
		if isinstance( CmdHandler, ScriptHandler ):
			content = CmdHandler.execute( folder )
			return content
		else: 
			return CmdHandler

	def join_contents( self, left_content, right_content ):
		if not isinstance( left_content, list ):
			left_content = [ left_content ]

		if not isinstance( right_content, list ):
			right_content = [ right_content ] 

		final_content = [ ( file1, file2 ) for file1 in left_content 
						  for file2 in right_content ]
		return final_content


class SingleCmdHandler:
	def __init__(self, cmd, optr):
		self.cmd = cmd
		self.optr = optr

	def execute_command( self, folder ):
		final_content = self._full_path_data( self.cmd, folder )
		final_content = [ final_content ] if not isinstance( final_content, list ) else final_content
		try:
			for cmd in final_content:
				if self.optr == CHDIR:
					trace_folder = os.path.join( folder, cmd )
					try:
						if os.path.isdir( trace_folder ):
							os.chdir( trace_folder )
						else: 
							with open(trace_folder, "r", encoding='utf-8') as read_file:
								print( read_file.read() )
					except Exception as error:
						print(error)

				elif self.optr == LIST_CONTENTS:
					list_path = os.path.join( folder, cmd )
					ExecUtils.list_contents( list_path )

				elif self.optr == INPUT:
					full_file = os.path.join( folder, cmd )
					if not os.path.exists(full_file):
						ExecUtils.create_file(full_file, cmd)
					ExecUtils.input_file(full_file)
				else: pass
			return True 
		except Exception as error:
			cprint(f"Execution Failed {error}", "red")
			return False

	def _full_path_data( self , CmdHandler, folder ):
		if isinstance( CmdHandler, ScriptHandler ):
			content = CmdHandler.execute( folder )
			return content
		else: 
			return CmdHandler

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
				cmd_length, push_node = getExpr( self.cmd_string, start_index ) or [0, None]
				if push_node:
					list_data.append( push_node )
					start_index = cmd_length

			elif self.cmd_string[ start_index ] == APPO:
				cmd_length, push_node = getUntil( self.cmd_string, start_index + 1, APPO ) or [0, None]
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
