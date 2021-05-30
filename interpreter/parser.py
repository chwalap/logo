from typing import Iterable
import ply.yacc as yacc
from interpreter.lexer import tokens, functions

precedence = (
  ('right', 'ASSIGN'),
  ('left', 'ADD', 'SUB'),
  ('left', 'MUL', 'DIV'),
  ('left', 'LSQUAREPAREN', 'RSQUAREPAREN'),
  ('left', 'LROUNDPAREN', 'RROUNDPAREN'),
  ('left', 'FUNC'),
  ('left', 'VAR'),
)

class AST(dict):
  counter = 0
  def __init__(self, *args, **kwargs):
    AST.counter += 1
    if AST.counter % 1000 == 0:
      print(AST.counter, "\n", flush=True) 

    def from_nested_dict(data):
      if not isinstance(data, dict):
        return data
      else:
        return AST({key: from_nested_dict(data[key]) for key in data})

    super(AST, self).__init__(*args, **kwargs)
    self.__dict__ = self

    for key in self.keys():
      self[key] = from_nested_dict(self[key])

# class AST:
#   def __init__(self, key, values=[]):
#     #self.type = key
#     self.children = {}
#     self.children[key] =
#     if is_collection(values):
      
#       for v in values:
#         print(v)
#         self.children[v.type] = v.children
#     else:
#       self.children = values

#   def __str__(self):
#     s = self.type.__str__() + "{ "
#     if is_collection(self.children):
#       s = ", ".join([ self.children[c].__str__() for c in self.children ])
#     else:
#       s = s + self.children.__str__() + " }"
    # return s

def p_program(p):
  'program : expr_list'
  p[0] = AST({ "program": p[1] })

# def p_code_list(p):
#   '''code_list : code
#                | code_list code'''
#   p[0] = [ p[len(p) - 1] ]
#   if len(p) == 3:
#     p[0] = p[1] + [ p[2] ]
#   print("p0:", p[0])

# def p_code(p):
#   '''code : expr_list'''
#           #| func_decl'''
#   p[0] = AST({ "code": p[1] })

def p_expr_num(p):
  'expr : number'
  p[0] = AST({ "expr": p[1] })

def p_expr_var(p):
  'expr : var'
  p[0] = AST({ "expr": p[1] })

def p_expr_func_call(p):
  'expr : func_call'
  p[0] = AST({ "expr": p[1] })
  
def p_expr_bin_op(p):
  '''expr : expr ADD expr
          | expr SUB expr
          | expr MUL expr
          | expr DIV expr'''
  p[0] = AST({ "expr": { p[2]: { "left": p[1], "right": p[3] } } })

def p_expr_paren(p):
  'expr : LROUNDPAREN expr RROUNDPAREN'
  p[0] = p[1]

def p_expr_assign(p):
  'var : var ASSIGN expr'
  print("assign:", p[1])
  p[1]["var"]["value"] = p[3]
  p[0] = p[1]
  print("assign var:", p[0])

def p_func_call(p):
  '''func_call : fname
               | fname farg_list'''
  if len(p) == 3:
    p[0] = AST({ "func_call": { "name": p[1], "arg_list": p[2] } })
  else:
    p[0] = AST({ "func_call": { "name": p[1], "arg_list": [] } })

def p_farg_list(p):
  '''farg_list : farg
               | farg_list farg'''
  p[0] = [ p[len(p) - 1] ]
  if len(p) == 3:
    p[0] = p[1] + [ p[2] ]

def p_farg(p):
  '''farg : number
          | var''' # todo: add func_call if possible
  p[0] = AST({ "farg": p[1] })

def p_number(p):
  'number : NUMBER'
  p[0] = AST({ "number": { "value": p[1] } })      

def p_var(p):
  'var : VAR'
  p[0] = AST({ "var": { "name": p[1], "value": float() } })

def p_fname(p):
  'fname : FUNC'
  p[0] = p[1]
  
def p_expr_list(p):
  '''expr_list : expr
               | expr_list expr'''
  p[0] = [ p[len(p) - 1] ]
  if len(p) == 3:
    p[0] = p[1] + [ p[2] ]

    
# def p_code(p):
#   '''code : main_expr
#           | main_expr code'''
#   code = p[1].children
#   if len(p) > 2:
#     code = code + p[2].children
#   p[0] = Node("code", code)

# def p_main_expr(p):
#   '''main_expr : fcall
#                | fbody'''
#   p[0] = Node("main_expr", [ p[1] ])

# def p_fdecl(p):
#   '''fdecl : TO fdef_ID
#            | TO fdef_ID args'''
#   p[0] = Node("fdecl",[ p[2:] ])


# def p_fbody(p):
#   'fbody : fdecl code fdef_END'
#   p[0] = Node("fbody", [ p[1:] ])

# def p_fcall(p):
#   '''fcall : ID
#            | ID args'''
#   p[0] = Node("fcall", [ p[1:] ])

# def p_expr_num(p):
#   'expression : NUMBER'
#   p[0] = Node("num", p[1])

# def p_expr_arg(p):
#   'expression : ARG'
#   p[0] = Node("arg", p[1])

# def p_expr_binop(p):
#   '''expression : expression ADD expression
#                 | expression SUB expression
#                 | expression MUL expression
#                 | expression DIV expression'''
#   p[0] = Node("binop", [ p[1], p[3], p[2] ])

# def p_expression_paren(p):
#   'expression : LROUNDPAREN expression RROUNDPAREN'
#   p[0] = Node("paren", [ p[2] ])
  
# # def p_loop(p): #  --------- ?>>
# #   'loop : LOOP NUMBER NUMBER LSQUAREPAREN code RSQUAREPAREN'
# #   start = p[2]
# #   end = p[3]
# #   code = p[5]
# #   p[0] = Node("loop", [ Node("loop_range", [ start, end ]), Node("loop_code", [ code ]) ])

# def p_fend(p):
#   'expression : END'
#   raise SyntaxError("No matching TO for this END: {}" % p)
  
# def p_args(p):
#   '''args : expression
#           | expression args'''
#   p[0] = Node("args", p[1:])

def p_error(p):
  print("Error:", p)
  if isinstance(p, AST):
    print(p.__str__())

parser = yacc.yacc()
