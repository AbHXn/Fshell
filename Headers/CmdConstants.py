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
FIND			= '@'

# didn't implemented
RE_APPEND 		= "=="
RE_ASSIGN		= "="

D_CMDS   = ( REMOVE, CREATE, COPY, CUT, RE_ASSIGN, RE_APPEND, FIND )
S_CMDS_A = ( LIST_CONTENTS, )
S_CMDS_B = ( INPUT, CHDIR )

BASE_DIR = '.'