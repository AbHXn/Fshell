A lightweight, custom DSL (Domain Specific Language) for managing and executing filesystem operations in Python. It supports creating, copying, moving, deleting files and folders, listing directory contents, and accepting user input with a small, scriptable command language.

---

## Usage

# Usage

## Directory
```
.!                             -> list current directory
*folder                        -> change directory
```

## Create
```
+ [file1 file2 file3]          -> create multiple files
+ file1 + file2 + file3        -> same as above

+ dir/ + [a/ b/]               -> create folder 'dir' with subfolders
dir + file                     -> create file inside dir
[dir a b] + [x y]              -> create x,y inside dir/, a/, b/
```

## Input / View
```
#file                          -> open file for input
#[file1 file2 file3]           -> open multiple files
*file                          -> print file contents
file1 = file2                  -> copy file1 to file2
file1 == file2                 -> append file1 content to file2
```

## Copy / Move
```
[file1 file2] += folder        -> copy files to folder
[file1 file2] -= folder        -> move files to folder

folder/ += dest                -> copy only CONTENTS of folder
folder += dest                 -> copy entire folder
```

## Path Storage
```
name -> $                      -> store current path as 'name'
&name += .                     -> copy stored-path contents here
```

## Stored Path Usage
```
path1 -> ./test/path1
path2 -> ./test/path2

[&path1 &path2] -= .           -> move stored folders here
```


---

## Requirements

* Python 3.8+
* [termcolor](https://pypi.org/project/termcolor/) for colored output

Install dependencies:

```bash
pip install termcolor
```

---

## Note

This tool is intended for educational and experimental purposes only.
File and folder operations performed using FileShell are irreversible — once deleted, they cannot be restored. Use with caution.

## License

This project is provided as-is, for educational and prototyping purposes. Use at your own risk.

---
