import ply.lex as lex

# Lexer states
states = (
   #('code', 'exclusive'),
   ('fdef', 'inclusive'),
#   ('lbody', 'inclusive'),
)

symbols = {
  'FORWARD' : "fw",
  'FW' : "fw",
  'BACKWARD' : "bw",
  'BW' : "bw",
  'RIGHT' : "rt",
  'RT' : "rt",
  'LEFT' : "lt",
  'LT' : "lt",
  #'SETXY', 'SETX', 'SETY',
  #'SETHOME', 'SETH',
  #'HOME',

  # queries
  # 'XCOR',
  # 'YCOR',
  # 'HEADING',
  # 'PENDOWN',
  # 'PENUP',
  # 'PENCOLOR',
  # 'PENSIZE',

  # # control
  # 'SHOW',
  # 'HIDE',
  # 'CLEAN',
  # 'CLEARSCREEN',
  # 'WRAP',
  # 'FILL',
  # 'SETPENDOWN',
  # 'SETPENUP',
  # 'SETPENPAINT',
  # 'SETPENERASE',
  # 'SETPENCOLOR',
  # 'SETPENSIZE',
}

functions = [
  'FORWARD', 'FW',
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
  'ARG',
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

  'IF',
  'LOOP',
  'TO',
  
  'ID',
  'END',
  'fdef_ID',
  'fdef_END',

  #others
  #'COMMENT',
]

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\+'
t_DIV = r'/'

t_ASSIGN = r'='

t_LROUNDPAREN  = r'\('
t_RROUNDPAREN  = r'\)'
t_LSQUAREPAREN = r'\['
t_RSQUAREPAREN = r'\]'

def t_fdef_END(t):
  r'(?i)end'
  t.lexer.pop_state()
  return t

def t_END(t):
  r'(?i)end'
  raise SyntaxError("No matching TO directive!")
  
t_LOOP = r'(?i)loop'
t_IF = r'(?i)if'

def t_NUMBER(t):
  r'[-+]?\d*\.?\d+|[-+]?\d+'
  t.value = float(t.value)    
  return t

def t_ARG(t):
  r'(?i)\:[a-zA-Z][\w+_]*'
  return t

def t_TO(t):
  r'(?i)to\ '
  print('dupaaaa')
  t.lexer.
  t.lexer.push_state('fdef')
  return t

def t_fdef_ID(t):
  r'(?i)[a-zA-Z][\w+_]*'
  return t

def t_ID(t):
  r'(?i)[a-zA-Z][\w+_]*'
  return t

def t_NEWLINE(t):
  r'\n+'
  t.lexer.lineno = len(t.value)

t_ignore = ' \t'
t_ignore_COMMENT = r'\;.*'

def t_error(t):
  print("Illegal character '%s' at:" % t.value[0], t.lineno)
  t.lexer.skip(1)

def find_column(input, token):
  line_start = input.rfind('\n', 0, token.lexpos) + 1
  return (token.lexpos - line_start) + 1

lexer = lex.lex()



# def t_LOOP(t):
#   r'''^ *(?:loop|LOOP)\s+(?'start'\d+)?\s+(?'end'\d+)\s+\[\s*+(?'lbody'(?:[^\]]|\n)*?)\s*\] *$'''
#   r'^ *loop /i'
#   t.loop.i_start = t.lex.start
#   t.loop.i_end = t.lex.end
#   if t.loop.i_start <= t.loop.i_end:
#     t.loop.lbody = t.lex.lbody
#     return t

  
#   #r'''^ *(?:to|TO) +(?'fname'\w+)(?'args'(?: *+\:[a-zA-Z_]\w*)*).*\n(?'fbody'(?:.*\n)*?) *(?:end|END) *?\n'''
#   t.value = lstrip(lstrip(str(t.lexer.fname))[2:])
#   return t

# def t_FN_CALL(t):
#   r'[a-zA-Z_][\w_]*'
#   #r'''^(?! *to( |\n)) *(?'fname'[a-zA-Z_]\w*) *(?'args'(?: *(?: *+\[(?: *\:?\w+)* *\])|(?: *+\:?\w+)*|(?:\s*+))) *\n'''
#   #r'''^(?!\s*to\s+) *(?'fname'[a-zA-Z_]\w*) *(?'args'(?: *\:?\w*)*)$'''
#   t.value = str(t.value)
#   return t

# currently all vars are also fn
# def t_VAR(t):
#   return t
#   r'\w+(\.\w+)?(\d+)?/i'
#   t.type = reserved.get(t.value, 'VAR')
#   return t