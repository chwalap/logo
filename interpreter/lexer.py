import ply.lex as lex

# Lexer states
# states = (
#    ('code', 'exclusive'),
#    ('fbody', 'inclusive'),
#    ('lbody', 'inclusive'),
#  )

# todo: add more reserved keywords
reserved = {
  'if' : 'IF',
  'loop' : 'LOOP'
}

# todo: add more functions
functions = [
  'FORWARD', 'FN',
  'BACKWARD', 'BW',
  'RIGHT', 'RT',
  'LEFT', 'LT',
  'SETXY', 'SETX', 'SETY',
  'SETHOME', 'SETH',
  'HOME',

  # queries
  'XCOR',
  'YCOR',
  'HEADING',
  'PENDOWN',
  'PENUP',
  'PENCOLOR',
  'PENSIZE',

  # control
  'SHOW',
  'HIDE',
  'CLEAN',
  'CLEARSCREEN',
  'WRAP',
  'FILL',
  'SETPENDOWN',
  'SETPENUP',
  'SETPENPAINT',
  'SETPENERASE',
  'SETPENCOLOR',
  'SETPENSIZE',
  #...
]

tokens = [
  # functions
  'FN_DECL',
  'FN_CALL',

  # arithmetic
  'VAR',
  'NUMBER',
  'ADD',
  'SUB',
  'MUL',
  'DIV',
  'ASSIGN',
  'LROUNDPAREN',
  'RROUNDPAREN',
  'LSQUAREPAREN',
  'RSQUAREPAREN',

  # condition
  'IF',

  # loop
  'LOOP',

  #others
  'COMMENT',
]

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\+'
t_DIV = r'/'

t_ASSIGN = r'='

#def t_LROUNDPAREN(t):


t_LROUNDPAREN  = r'\('
t_RROUNDPAREN  = r'\)'
t_LSQUAREPAREN = r'\['
t_RSQUAREPAREN = r'\]'

t_LOOP = r'loop/i'
t_IF = r'if/i'

# def t_LOOP(t):
#   r'''^ *(?:loop|LOOP)\s+(?'start'\d+)?\s+(?'end'\d+)\s+\[\s*+(?'lbody'(?:[^\]]|\n)*?)\s*\] *$'''
#   r'^ *loop /i'
#   t.loop.i_start = t.lex.start
#   t.loop.i_end = t.lex.end
#   if t.loop.i_start <= t.loop.i_end:
#     t.loop.lbody = t.lex.lbody
#     return t


t_FN_DECL = r'to/i'
  
#   #r'''^ *(?:to|TO) +(?'fname'\w+)(?'args'(?: *+\:[a-zA-Z_]\w*)*).*\n(?'fbody'(?:.*\n)*?) *(?:end|END) *?\n'''
#   t.value = lstrip(lstrip(str(t.lexer.fname))[2:])
#   return t

def t_FN_CALL(t):
  r'[a-zA-Z_][\w_]*/i'
  #r'''^(?! *to( |\n)) *(?'fname'[a-zA-Z_]\w*) *(?'args'(?: *(?: *+\[(?: *\:?\w+)* *\])|(?: *+\:?\w+)*|(?:\s*+))) *\n'''
  #r'''^(?!\s*to\s+) *(?'fname'[a-zA-Z_]\w*) *(?'args'(?: *\:?\w*)*)$'''
  t.value = str(t.value)
  return t

# currently all vars are also fn
# def t_VAR(t):
#   return t
#   r'\w+(\.\w+)?(\d+)?/i'
#   t.type = reserved.get(t.value, 'VAR')
#   return t

def t_NUMBER(t):
  r'[-+]?\d*\.?\d+|[-+]?\d+'
  t.value = float(t.value)    
  return t

def t_newline(t):
  r'\n+'
  t.lexer.lineno += len(t.value)

t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)

def find_column(input, token):
  line_start = input.rfind('\n', 0, token.lexpos) + 1
  return (token.lexpos - line_start) + 1

lexer = lex.lex()
