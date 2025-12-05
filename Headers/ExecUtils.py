import os
from termcolor import cprint, colored
import time
import shutil

class ExecUtils:
	@staticmethod
	def print_dir_structure( dir_path, Msg, think_time = False ):	
		if not isinstance( dir_path, str ):
			raise TypeError( "Invalid Directory Argument" )
		
		try:
			dir_path = dir_path.strip()

			if dir_path == '': return 
			
			for dirs, _, files in os.walk( dir_path ):
				for file in files:
					if think_time: 
						time.sleep( 0.2 )
					
					full_path = os.path.join( dirs, file )
					cprint( f"{Msg}: {full_path}" , "green")
			
			if think_time: # a small time to think
				time.sleep( 2 )

		except Exception as _:
			pass


	@staticmethod
	def create_file( base, name ):
		if not isinstance( base, str ) or not isinstance( name, str ):
			raise TypeError( "File path should be a string" )

		try:
			base, name = base.strip(), name.strip()
			path = os.path.join( base, name )

			if path == '': return 

			if name.endswith( os.sep ):
				os.makedirs( path, exist_ok=True )
			else:
				os.makedirs( base, exist_ok=True )
				if not os.path.exists( path ):
					with open(path, "w") as file:
						pass
				else:
					raise FileExistsError( "File already exists" )

		except Exception as e:
			cprint( f"File Creation Failed: {e}", "red" )

	@staticmethod
	def remove_file( path ):
		try:
			path = path.strip()	

			if path == '':
				return 		

			if os.path.isdir( path ):
				ExecUtils.print_dir_structure( path, "Removing", think_time = True )
				shutil.rmtree( path )
			
			elif os.path.exists( path ):
				cprint( f"Removing: {path}", "green" )
				time.sleep( 2 )
				os.remove( path )

			else: 
				FileNotFoundError( "Failed to remove file" )

		except Exception as e:
			cprint( f"File Remove Error: {e}", "red" )

	@staticmethod
	def copy_file( src, dst ):
		if not isinstance( src, str ) or not isinstance( dst, str ):
			raise TypeError( "File path should be a string" )

		try:
			src, dst = src.strip( ), dst.strip( )

			if os.path.exists( dst ) and os.path.isdir( dst ):
				if os.path.isdir( src ): # if src is a directory
					ExecUtils.print_dir_structure( src, "Copying: " )

					shutil.copytree( src, os.path.join( dst,
							os.path.basename( src ) ), dirs_exist_ok=True )
				else:
					os.makedirs( dst, exist_ok=True )
					shutil.copy2( src, os.path.join( dst, os.path.basename( src ) ) )
			else: 
				with open( dst, "w", encoding='utf-8' ) as file_w:
					with open( src, "r", encoding="utf-8" ) as file_r:
						file_w.write( file_r.read() )

		except Exception as e:
			cprint( f"File Copy Error: {e}", "red" )

	@staticmethod
	def move_file( src, dst ):
		if not isinstance( src, str ) or not isinstance( dst, str ):
			raise TypeError( "File path should be a string" )

		try:
			src, dst = src.strip(), dst.strip()
			if src == '' or dst == '':
				return

			if os.path.exists( src ) and os.path.exists( dst ):
				ExecUtils.print_dir_structure( src, "Moving" )
				shutil.move( src, dst )
			else: 
				os.rename(src, dst)

		except Exception as e:
			cprint( f"File Move Error: {e}" , "red")

	@staticmethod
	def list_contents( folders, BASE_DIR ):
		if not isinstance( folders, list ):
			folders = [ ( BASE_DIR, folders ) ]
		try:
			for parent, child in folders:
				folder = os.path.join( parent, child ) 
				cprint(f"Listing: {child}:", "green")

				if os.path.exists( folder ) and os.path.isfile( folder ):
					with open( folder, "r", encoding="utf-8" ) as txt_file:
						print( txt_file.read() )
					return

				with os.scandir( folder ) as d_files:
					for file in d_files:
						name = file.name
						name = colored(name, 'blue') if file.is_dir() else name
						print(f"{name}", end="  ")
					print()

		except Exception as e:
			cprint( f"Listing Error: {e}", "red" )

	@staticmethod
	def input_file( file_name ):
		if not isinstance( file_name, str ):
			raise TypeError( "Filname should be a str" )

		print(f"Enter text for {file_name} (Ctrl+C to save):")
		try:
			with open(file_name, "w", encoding='utf-8') as w_file:
				while True:
					line = input()
					w_file.write(line + '\n')
		
		except KeyboardInterrupt:
			cprint( "File Saved", "green" )
	
	@staticmethod
	def list_files_given( folders, files ):
		if not isinstance( folders, list ):
			folders = [ folders ]
		try:
			files_script = False
			if isinstance( files, str ):
				files = [ files ]
			elif isinstance( files, list ) or isinstance( files, tuple ):
				pass
			else: files_script = True;

			for folder in folders:
				if files_script:
					files = files.execute( folder );

				with os.scandir( folder ) as d_files:
					for file in d_files:
						
						if not any( sfile in file.name for sfile in files ):
							continue

						name = file.name
						name = colored(name, 'light-green') if file.is_dir() else name
						print(f"{name}", end="  ")
					print()

		except Exception as e:
			cprint( f"Listing Error: {e}", "red" )
