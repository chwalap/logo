import ply.lex as lex

# todo: add more reserved keywords
reserved = {
  'if' : 'IF',
  'loop' : 'LOOP'
}

# todo: implement regexes for all tokens
tokens = [
  # turtle
  'FORWARD',
  'BACKWARD',
  'RIGHT',
  'LEFT',
  'SETXY',
  'SETX',
  'SETY',
  'SETH',
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

  # arithmetic
  #'VAR',
  'NUMBER',
  'ADD',
  'SUB',
  'MUL',
  'DIV',
  'ASSIGN',
  'LPAREN',
  'RPAREN',

  # condition
  'IF',
  #...

  # loop
  'LOOP',
  'LOOP_BEGIN',
  'LOOP_END',

  #others
  'COMMENT',
]

t_FORWARD  = r'FORWARD|FD'
t_BACKWARD = r'BACK|BK'
t_RIGHT    = r'RIGHT|RT'
t_LEFT     = r'LEFT|LT'

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\+'
t_DIV = r'/'
t_ASSIGN = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

t_LOOP = r'LOOP'
t_LOOP_BEGIN = r'\['
t_LOOP_END = r'\]'

#def t_VAR(t):
  #return t
  #r'[A-Za-z][\w$]*(\.[\w$]+)?(\[\d+])?'
  #t.type = reserved.get(t.value, 'VAR')
  #return t

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
