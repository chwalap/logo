
import ply.yacc as yacc

from interpreter.lexer import tokens, functions

precedence = (
  ('left', 'ADD', 'SUB'),
  ('left', 'MUL', 'DIV'),
  ('left', 'LSQUAREPAREN', 'RSQUAREPAREN'),
  ('left', 'LROUNDPAREN', 'RROUNDPAREN'),
  ('left', 'ARG', 'NUMBER', 'ID'),
  #('left', 'NEWLINE'),
)

variables = {}

class Node:
  def __init__(self, type, children=[]):
    self.type = type
    self.children = children

  def __str__(self):
    return self.type.__str__() + "(" + ", ".join([c.__str__() for c in self.children]) + ")"
    
def p_code(p):
  '''code : main_expr
          | main_expr code'''
  code = p[1].children
  if len(p) > 2:
    code = code + p[2].children
  p[0] = Node("code", code)

def p_main_expr(p):
  '''main_expr : fcall
               | fdecl
               | loop'''
  p[0] = Node("main_expr", [ p[1] ])

def p_fdecl(p):
  '''fdecl : FN_DECL ID code fend
           | FN_DECL ID args code fend'''
  args = p[2:]
  args.pop()
  code = args.pop()
  fname = args.pop(0)
  functions[fname] = p[0] = Node("fdecl", [ Node("fsignature", [ fname, args ]), Node("fnbody", [ code ]) ])

def p_fcall(p):
  '''fcall : fname
           | fname args'''
  p[0] = Node("fcall", p[1:])

def p_expr_num(p):
  'expression : NUMBER'
  p[0] = Node("num", [ p[1] ])

def p_expr_arg(p):
  'expression : ARG'
  p[0] = Node("arg", [ p[1] ])

def p_expr_binop(p):
  '''expression : expression ADD expression
                | expression SUB expression
                | expression MUL expression
                | expression DIV expression'''
  p[0] = Node("binop", [ p[1], p[3], p[2] ])

def p_expression_paren(p):
  'expression : LROUNDPAREN expression RROUNDPAREN'
  p[0] = Node("paren", [ p[2] ])
  
def p_loop(p): #  --------- ?>>
  'loop : LOOP NUMBER NUMBER LSQUAREPAREN code RSQUAREPAREN'
  start = p[2]
  end = p[3]
  code = p[5]
  p[0] = Node("loop", [ Node("loop_range", [ start, end ]), Node("loop_code", [ code ]) ])

def p_fname_id(p):
  'fname : ID'
  if str(p[1]).upper() == "TO":
    raise KeyError("Function can't be named 'TO'!")
  p[0] = Node("fname", [ p[1] ])

def p_fend(p):
  'fend : END'
  p[0] = Node("fend", [ p[1] ])
  
def p_args(p):
  '''args : expression
          | expression args'''
  p[0] = Node("args", p[1:])

def p_error(p):
  print("Error:", p)
  if isinstance(p, Node):
    print(p.__str__())

parser = yacc.yacc()
