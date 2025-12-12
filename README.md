A lightweight, custom DSL (Domain Specific Language) for managing and executing filesystem operations in Python. It supports creating, copying, moving, deleting files and folders, listing directory contents, and accepting user input with a small, scriptable command language.

---

## Features

* **Custom DSL commands** for filesystem operations.
* Execute scripts with expressions (`{}`) and lists (`[]`).
* Supports regex-based file matching.
* Handles both files and folders.
* Interactive input mode for writing files.
* Colorful console output using `termcolor`.
* Cross-platform support (Windows, Linux).

---

## Usage

# Usage

When FileShell starts, you will see:

```
2025-12-12@FSHELL::/home/system404/backup_fedora/Fshell$
```

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


## Notes

* File operations are **destructive** — use caution with remove or move commands.
* Regex patterns are applied to filenames for filtering.
* Nested lists and expressions are supported but complex scripts may require careful formatting.
* Works best in a dedicated project folder to avoid accidental file changes.

---

## Requirements

* Python 3.8+
* [termcolor](https://pypi.org/project/termcolor/) for colored output

Install dependencies:

```bash
pip install termcolor
```

---

## Limitations

* No sandboxing for destructive commands — files can be overwritten or deleted.
* Global working directory changes (`chdir`) can affect the process.
* Parser is basic and may fail with malformed expressions or deeply nested structures.
* Regex patterns should be simple to avoid performance issues.

---

## License

This project is provided as-is, for educational and prototyping purposes. Use at your own risk.

---

Would you like me to also **add a small diagram showing command flow and handler classes**? It will make the README more visual and easier to understand.
