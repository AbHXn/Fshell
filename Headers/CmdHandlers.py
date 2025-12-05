from .ExecUtils import ExecUtils
from termcolor import cprint
from .CmdConstants import *
import os
import re

def _full_path_data( CmdHandler, folder ):
	if isinstance( CmdHandler, ScriptHandler ):
		content = CmdHandler.execute( folder )
		return content
	else: 
		return CmdHandler

class ScriptHandler:
	def __init__(self, script):
		self.script = script

	def execute(self, folder):
		try:
			raise
		except Exception as e:
			cprint(f"Script execution failed: {e}", "red")
			return []

class DoubleCmdHandler:
	def __init__(self, left, right, optr):
		self.left  = left
		self.right = right
		self.optr = optr

	def execute_command( self, currentFolder ):
		leftFiles 	 =_full_path_data( self.left, currentFolder )
		righFIles    =_full_path_data( self.right, currentFolder )
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

			elif self.optr == FIND:
				ExecUtils.list_files_given( righFIles, self.left )

		return True

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
		final_content = _full_path_data( self.cmd, folder )
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
					ExecUtils.list_contents( list_path, BASE_DIR )

				elif self.optr == INPUT:
					full_file = os.path.join( folder, cmd )
					if not os.path.exists(full_file):
						ExecUtils.create_file( folder , cmd)
					ExecUtils.input_file(full_file)
				else: pass
			return True 
		except Exception as error:
			cprint(f"Execution Failed {error}", "red")
			return False
