from datetime import date
import subprocess
import os
import shutil

REMOVE      = '-'
CREATE      = '+'
COPY        = '+='
CUT         = '-='
CHDIR       = '*'
INPUT       = '#'
EXPR_OPEN   = '{'
EXPR_CLOSE  = '}'
LIST_OPEN   = '['
LIST_CLOSE  = ']'
LIST_CONTENTS = '!'

class Status:
	def __init__(self, optr, data):
		self.optr = optr
		self.data = data

class Node:
	def __init__(self, status, parent = None):
		self.status = status
		self.children = []
		self.parent = parent

	def add_child(self, child):
		self.children.append(child)

class Script:
	def __init__(self, code):
		self.code = code

	def execute(self, folder):
		try:
			dir_files = os.listdir(folder)
			self.code = self.code.replace('*', str(dir_files))
			results = eval(self.code)
			return [line.strip() for line in results
						 if line.strip()]
		except Exception as e:
			print("Script execution failed:", e)
			return []
			
#### END OF CLASS

def is_operator(optr):
	return optr in {REMOVE, CREATE, CUT, COPY, CHDIR, INPUT}

def input_file(file_name):
	print(f"Enter text for {file_name} (Ctrl+C to save):")
	try:
		with open(file_name, "w", encoding='utf-8') as w_file:
			while True:
				line = input()
				w_file.write(line + '\n')
	except KeyboardInterrupt:
		print("\nFile Saved.")

def create_file(base, name):
	try:
		if name == "": 
			return False

		path = os.path.join(base, name)
		if name.endswith('/') or name.endswith(os.sep):
			os.makedirs(path, exist_ok=True)
		else:
			os.makedirs(os.path.dirname(path), exist_ok=True)
			if not os.path.exists(path):
				with open(path, "w") as file:
					pass
		return True
	except Exception:
		return False

def remove_file(path):
	try:
		if os.path.isdir(path):
			shutil.rmtree(path)
		elif os.path.exists(path):
			os.remove(path)
		return True
	except Exception:
		return False

def copy_file(src, dst):
	try:
		if os.path.exists(dst) and os.path.isdir(dst):
			if os.path.isdir(src):
				shutil.copytree(src, 
					os.path.join(
						dst, 
						os.path.basename(src)), 
						dirs_exist_ok=True)
			else:
				os.makedirs(dst, exist_ok=True)
				shutil.copy2(src, 
					os.path.join(dst, os.path.basename(src)))
		else: os.rename(src, dst)
		return True
	except Exception:
		return False

def move_file(src, dst):
	try:
		if os.path.exists(src) and os.path.exists(dst):
			shutil.move(src, dst)
		else:
			os.rename(src, dst)
		return True
	except Exception:
		return False

def join(data1, data2):
	if not isinstance(data1, list):
		data1 = [data1]
	if not isinstance(data2, list):
		data2 = [data2]
	return [(a, b) for a in data1 for b in data2]

def build_command_tree(commands, root=None):
	for cmd in commands:
		optr = cmd.optr
		if root is None:
			root = Node(cmd)
		else:
			if optr in (CHDIR, COPY, CUT):
				child = root
				if optr != CHDIR:
					child.status.optr = optr
					cmd.optr = None
				else:
					child.status.optr = optr
				root = Node(cmd)
				child.parent = root
				root.add_child(child)
			else:
				root.add_child(Node(cmd, parent=root))
	return root

def get_high_depth_node(croot, depth=0):
	for children in croot.children:
		if children.children:
			return get_high_depth_node(children, depth+1)
	return croot

def list_contents(folder):
	try:
		if os.path.exists(folder) and os.path.isfile(folder):
			with open(folder, "r", encoding="utf-8") as txt_file:
				print(txt_file.read())
			return
		with os.scandir(folder) as d_files:
			for file_ in d_files:
				name = file_.name
				name = name +'/' if file_.is_dir() else name
				print(f"\t{name}")
	except Exception as error:
		print(error)

def execute_command_tree(croot, proot, folder_trace):
	if not croot: return

	if not proot and not croot.children and croot.status.optr == CHDIR:
		try:
			if os.path.isdir(croot.status.data):
				os.chdir(croot.status.data)
			else: 
				with open(croot.status.data, "r", encoding='utf-8') as read_file:
					print(read_file.read())
		except Exception as error:
			print(error)
		return

	real_path = os.path.join(folder_trace, croot.status.data)

	if croot.status.optr == LIST_CONTENTS:
		list_contents(real_path)

	if croot.status.optr in (CHDIR, CUT, COPY):
		folder_trace = real_path

	for node in croot.children:
		if node == proot:
			continue

		parent = node.parent
		data = node.status.data
		op = node.status.optr

		if isinstance(data, Script):
			try:
				data = data.execute('.')
			except Exception as error:
				print(error)

		if op == LIST_CONTENTS:
			list_contents(os.path.join(real_path, data))
			continue

		pairs = join(real_path, data)

		for pdata, cdata in pairs:
			current = os.path.join(pdata, cdata) \
				if isinstance(cdata, str) else pdata

			if op == CREATE:
				if not os.path.exists(current):
					create_file(pdata, cdata)
				else: print(f"{cdata} already exists.")

			elif op == REMOVE:
				if os.path.exists(current):
					remove_file(current)
				else: print(f"{cdata} not found.")

			elif op == INPUT:
				if not os.path.exists(current):
					create_file(pdata, cdata)
				input_file(current)

			elif op in (COPY, CUT):
				if not os.path.exists(pdata):
					os.makedirs(pdata, exist_ok=True)
				if os.path.exists(cdata):
					if op == COPY: 
						copy_file(cdata, pdata)
					else: move_file(cdata, pdata)
				else: print(f"Source {cdata} not found.")

	execute_command_tree(croot.parent, croot, folder_trace)

def get_commands(line):
	if not line.strip():
		return None

	cmds = line.strip().split()
	operator = None
	results, lists = [], []
	expr_script = ''
	list_mode = False
	expr_mode = False

	for token in cmds:
		if expr_mode:
			if token.endswith(EXPR_CLOSE):
				expr_script += ' ' + token[:-1]
				results.append(Status(operator, Script(expr_script.strip())))
				expr_mode = False
				operator = None
				expr_script = ''
			else:
				expr_script += ' ' + token

		elif list_mode:
			if token.endswith(LIST_CLOSE):
				lists.append(token[:-1])
				results.append(Status(operator, lists.copy()))
				lists.clear()
				list_mode = False
				operator = None
			else:
				lists.append(token)

		elif token.startswith(CHDIR):
			results.append(Status(CHDIR, token[1:]))

		elif token.endswith(LIST_CONTENTS):
			results.append(Status(LIST_CONTENTS, token[:-1]))

		elif is_operator(token):
			operator = token

		elif token.startswith(INPUT):
			results.append(Status(INPUT, token[1:]))

		elif token.startswith(LIST_OPEN):
			list_mode = True
			if len(token) > 1:
				lists.append(token[1:])

		elif token.startswith(EXPR_OPEN):
			expr_mode = True
			if len(token) > 1:
				expr_script += token[1:]

		else:
			results.append(Status(operator, token))
			operator = None

	root = build_command_tree(results)
	high_depth_node = get_high_depth_node(root)
	execute_command_tree(high_depth_node, None, '.')

def main():
	print("\n**** COMMAND CANNOT BE REVERSED, VERIFY BEFORE RUNNING... ****\n")
	print("Scripts will be executed on current folders...\n")

	while True:
		try:
			get_commands(input(f"{date.today()}: "))
		except KeyboardInterrupt:
			print("\nExiting shell.")
			break
		except Exception as e:
			print("Error:", e)


if __name__ == "__main__":
	main()
