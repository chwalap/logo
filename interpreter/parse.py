import inspect
from io import UnsupportedOperation
from re import DEBUG
import turtle
import ply.yacc as yacc
from interpreter.lexer import tokens
import copy
from interpreter.logo import *


# Helpers
class StackCorruption(Exception):
  pass

def does_function_have_return(func):
  lines, _  = inspect.getsourcelines(func)
  return any("return" in line for line in lines)

def logo_make(name, value):
  print(f'Inside logo_make({name}, {value})')
  vars[name] = value

def logo_thing(name):
  print(f'Inside logo_thing({name})')
  return vars[name]

def logo_print(text):
  print(f'Inside logo_print({text})')
  print(text)

def new_scope(prev_scope, args):
  s = copy.deepcopy(prev_scope)
  for k, v in args:
    s["variables"][k] = v
  return s


# Operators precedence
precedence = (
  ('left', 'WORD'),
  ('left', 'NUMBER'),
  ('nonassoc', '=', 'NOT_EQUAL'),
  ('left', '^'),
  ('left', '+', '-'),
  ('left', '*', '/', '%'),
  ('right', ':', '"'),
)


# Internal interpreter state
proc_stack = []
scopes = []

scopes.append(new_scope({ "variables": {}, "procedures": {} }, {}))
vars = (lambda: scopes[-1]["variables"])()
procs = (lambda: scopes[-1]["procedures"])()


# Initialize turtle
screen = turtle.Screen()
screen.setup(width=800, height=640)
screen.title('Logo programming language interpreter')
turtle.mode("logo")
t = turtle.Turtle()


# Add some functions from the turtle library
# todo: lead them dynamically from the module
procs["forward"] = t.forward
procs["backward"] = t.backward
procs["right"] = t.right
procs["left"] = t.left
procs["show"] = t.showturtle
procs["hide"] = t.hideturtle
procs["setcolor"] = t.color
procs["make"] = logo_make
procs["thing"] = logo_thing
procs["print"] = logo_print

# Yeah... this can't be our main recipem, it block others
# Procedure statement - may be constructed with many procedures in a row
# Manually handled by handle_prev_word to resolve LOGO ambigous syntax
def p_procedure_statement(p):
  '''procedure_statement : word handle_prev_word procedure_statement
                         | word word-list handle_prev_word'''
  print(f'p_procedure_statement: word: {p[1]}, handle_prev_word: {p[2]}')

def p_handle_prev_word(p):
  'handle_prev_word : '

  method_list = [func for func in dir(yacc.YaccSymbol) if callable(getattr(yacc.YaccSymbol, func))]

  print(all)

  token = p[-1]
  print(f'Handling previous word: {token}')

  # Handle procedures 
  if token in procs:

    proc_stack.append(token)
    lvl = len(proc_stack)

    procedure = procs[token]
    does_return = does_function_have_return(procedure)
    no_parsed_params_required = len(inspect.getfullargspec(procedure).args)
    
    # Feed with tokens one by one
    def eof_feeder(tok):
      if len(params) < no_parsed_params_required:
        return clexer.token()
      return None

    # Clone lexer twice, first for us to save the state of our lexer (is it needed?)
    # And second for inner parser, then save starting position and replace eof function
    clexer = p.lexer.clone()
    ilexer = p.lexer.clone()
    start_pos = clexer.lexpos
    clexer.lexeoff = eof_feeder

    tokens = [ ]
    params = [ ]

    print("(lvl: ", lvl, " going one lvl deeper!") 
    i = 0
    while len(params) < no_parsed_params_required:

      print("while iteration: ", i)
      i = i + 1

      # add another token
      tokens.append(str(ilexer.token().value))

      inner_parser = yacc.yacc()

      result = inner_parser.parse(lexer=clexer, tokenfunc=lambda:None, debug=True, tracking=True)
      print("(lvl: ", lvl, ") parsed token: ", tokens[-1], "; result: ", result)
      params.append(result)

      print("(lvl: ", lvl, ") current params: ", params)

    print("(lvl: ", lvl, ") after while; params: ", params, "; tokens: ", tokens)

    # flexer = p.lexer.clone()
    # # while shouyld be good
    # content = str([ flexer.lexdata[pos] for pos in range(start_pos - 1, clexer.lexpos) ])
    # print("Content: ", content)

    print(f'Calling turtle procedure {token} with arguments {params} from LOGO interpreter')

    # todo: handle lists as parameters

    # todo: is it needed?
    if does_return:
      p[0] = procedure(*params)
    else:
      procedure(*params)

    if proc_stack.pop() != token:
      raise StackCorruption()
    lvl = len(proc_stack)

  # Handle variables
  elif token in vars:

    p[0] = vars[token]

  # Otherwise act like you'd the previous word
  else:
    p[0] = token

def get_binary_operator_fn(op):
  if op == '+': return lambda x,y: x+y
  elif op == '-': return lambda x,y: x-y
  elif op == '*': return lambda x,y: x*y
  elif op == '/': return lambda x,y: x/y
  elif op == '%': return lambda x,y: x%y
  elif op == '^': return lambda x,y: pow(x, y)
  else: raise UnsupportedOperation(f"Unknown operator: {op}")

# Arithmetic operators for numbers
def p_arithmetic_binary_operator(p):
  '''number : number '+' number
            | number '-' number
            | number '*' number
            | number '/' number
            | number '%' number
            | number '^' number'''
  p[0] = get_binary_operator_fn(p[2])(float(p[1]), float(p[3]))

def p_words_first(p):
  'words : word'
  p[0] = p[1]

def p_words_extend(p):
  'words : words word'
  p[0] = p[1]
  p[0].append(p[2])

def p_word_list(p):
  '''word-list : '[' words ']'
               | '[' word-list ']' '''
  p[0] = p[2]

def p_number(p):
  'number : NUMBER'
  p[0] = p[1]

# def p_word_number(p):
#   'word : NUMBER'
#   p[0] = p[1]

def p_word_equal(p):
  '''word : word '=' word'''
  p[0] = ( p[1] == p[3] )

def p_word_not_equal(p):
  'word : word NOT_EQUAL word'
  p[0] = ( p[1] != p[3] )

def p_word_value(p):
  '''word : ':' WORD'''
  p[0] = vars[p[2]]

def p_word_name(p):
  '''word : '"' WORD'''
  p[0] = p[2]

def p_word(p):
  'word : WORD'
  p[0] = p[1]
  
def p_empty(p):
  'empty :'
  pass

def p_error(p):
  if p is not None:
    print("Syntax Error:", p.__str__())

parser = yacc.yacc(debug=True)

def run_parser(input):
  parser.parse(input, debug=True, tracking=True)

# precedence = (
#   ('nonassoc', 'EQUAL', 'NOT_EQUAL', 'LT', 'LE', 'GT', 'GE'),
#   ('nonassoc', 'NUMBER', 'WORD', 'TRUE', 'FALSE'),
#   ('left', '+', '-'),
#   ('left', '*', '/', '%'),
#   ('left', '^'),
#   ('left', 'OR'),
#   ('left', 'AND'),
#   ('right', 'NOT'),
#   ('left', 'ADD', 'SUB'),
#   ('left', 'MUL', 'DIV', 'MOD'),
#   ('left', 'POW'),
#   # ('left', '[', ']'),
#   ('left', '(', ')'),
#   ('right', ':', '"'),
#   ('right', 'UMINUS'),
# #  ('left', 'MAKE', 'THING'),
# )
#   #('nonassoc','IF', 'IFELSE', 'REPEAT', 'TO', 'TO_NAME'

# def get_binary_operator_fn(op):
#   if op in ['+', 'ADD']: return lambda x,y: x+y
#   elif op in ['-', 'SUB']: return lambda x,y: x-y
#   elif op in ['*', 'MUL']: return lambda x,y: x*y
#   elif op in ['/', 'DIV']: return lambda x,y: x/y
#   elif op in ['%', 'MOD']: return lambda x,y: x%y
#   elif op in ['^', 'POW']: return lambda x,y: pow(x, y)


# def new_scope(prev_scope, args):
#   s = copy.deepcopy(prev_scope)
#   for k, v in args:
#     s["variables"][k] = v
#   return s

# scopes = []
# scopes.append(new_scope({ "variables": {}, "procedures": {} }, {}))

# vars = (lambda: scopes[-1]["variables"])()
# procs = (lambda: scopes[-1]["procedures"])()

# screen = turtle.Screen()
# turtle.mode("logo")
# screen.setup(width=800, height=640)
# screen.title('Logo programming language interpreter')
# t = turtle.Turtle()



# # def load_known_procedures():
#   # print(inspect.getmembers(turtle))
#   # for name, val in inspect.getmembers(turtle):
#   #   print(name)
#   #   if callable(val):
#   #     print(name)
#   #     procs[name] = val
#   #     if name == "forward":
#   #       print(inspect.getmembers(val))

  
# def logo_make(name, value):
#   vars[name] = value

# def logo_thing(name):
#   return vars[name]

# def logo_print(text):
#   print(text)

# procs["forward"] = t.forward
# procs["backward"] = t.backward
# procs["right"] = t.right
# procs["left"] = t.left
# procs["show"] = t.showturtle
# procs["hide"] = t.hideturtle
# procs["setcolor"] = t.color
# procs["make"] = logo_make



# procs["make"]('asd', 5)
  



# def run_parser(input):
#   parser.parse(input, debug=True, tracking=True)
#   # loop()

# # def fn_call(p):
# #   fname = str(p[1]).lower()
# #   args = tuple(p[2:])

# #   print("fname", fname)
# #   print("args", args)

# #   # first try LOGO procedures from the library
# #   # after that try with user defined procedures
# #   if hasattr(turtle, fname):
# #     fn = getattr(turtle, fname)
# #   elif fname in procs:
# #     fn = procs[fname]
# #   else:
# #    raise NotImplementedError("procedure {} not implemented" % fname)

# #   if len(signature(fn).parameters) == 0:
# #     p[0] = fn()
# #   else:
# #     p[0] = fn(*args)
# #   print("procedure",fname,"returned",p[0])

# # ==================================

# # Control Statements

# def p_statements(p):
#   '''statements : statement
#                 | statement statements'''
#   pass

# # To statement
# def p_to_statement(p):
#   'statement : TO TO_NAME TO_ARGS TO_CODE'
#   print(p[1], p[2], p[2], sep='\n')
  
# def p_to_statement_no_args(p):
#   'statement : TO TO_NAME TO_CODE'
#   print(p[1], p[2], p[2], sep='\n')

# def p_to_args(p):
#   '''TO_ARGS : TO_ARGS TO_ARG
#              | TO_ARG'''
#   if len(p) == 3:
#     p[0] = [ p[2] ] + p[1]
#   else:
#     p[0] = [ p[1] ]
#   print(p[0])

# # If statement
# # def p_if_statement_execution(p):
# #   '''statement : bool_expression '[' statements ']' '''
# #   if bool(p[1]): # hmmm?
# #     print("statements #1 executed")

# # def p_ifelse_statement_execution(p):
# #   '''statement : bool_expression '[' statements ']' '[' statements ']' '''
# #   if bool(p[1]): # hmmm
# #     print("statements #1 executed")
# #   else:
# #     print("statements #2 executed")

# # def p_if_statement(p):
# #   '''expression : IF bool_expression'''
# #   p[0] = p[1]

# # def p_if_statement_v2(p):
# #   '''expression : IF '[' bool_expression ']' '''
# #   p[0] = p[1]

# # def p_ifelse_statement(p):
# #   '''expression : IFELSE bool_expression'''
# #   p[0] = p[1]

# # def p_ifelse_statement_v2(p):
# #   '''expression : IFELSE '[' bool_expression ']' '''
# #   p[0] = p[1]

# # Repeat statement ---> not finished yet... # maybe copy the parser?
# # def p_repeat(p):
# #   '''statement : REPEAT arithmetic_expression '[' statements ']' '''
# #   n = int(p[2])

# # def p_statement_procedure_call(p):
# #   'statement : procedure_call'



# # def p_empty_words(p):
# #   'words : empty'
# #   p[0] = [ ]
  
# # def p_words_all(p): # get number or procedure
# #   '''words : word
# #            | words word
# #            | procedure_call'''
# #   p[0] = [ p[len(p) - 1] ]
# #   if len(p) == 3:
# #     p[0] = p[1] + [ p[2] ]

# # def p_procedure_call(p):
# #   '''procedure_call : word '(' words ')' '''
# #   print('word: ', p[1])
# #   print('words: ', p[3])

# # def p_procedure_call(p):
# #   '''statement : word
# #                | word statement
# #                | '(' statement ')'
# #                | statement '(' statement ')'
# #                | NEWLINE'''
# #   print(p[1]) 


# def p_word(p):
#   '''word : WORD'''
#   p[0] = str(p[1])

# def p_word_number(p):
#   '''number : NUMBER'''
#   p[0] = float(p[1])

# def p_num_word(p):
#   '''word : NUMBER'''
#   p[0] = p[1]
  
# def p_word_name(p):
#   '''word : '"' word'''
#   p[0] = str(p[1])

# def p_word_value(p):
#   '''word : ':' word'''
#   p[0] = vars[ p[2] ]

# # def p_word_word(p):
# #   '''word : word word'''
# #   p[0] = [ p[1], p[2] ]

# # def p_word_in_brackets(p):
# #   ''' '(' word ')' : '(' word ')' '''
# #   pass

# # def p_word(p):
# #   '''word : WORD
# #           | NUMBER
# #           | '"' word
# #           | ':' word
# #           | word word'''
  
#   '''expression : word '(' ')'
#                 | word '(' word ')'
#                 | word '(' expression ')' '''

# # def p_expression_expression(p):
# #   'expression : expression expression'
# #   p[0] = [ p[1], p[2] ]

   
# def p_procedure_call(p):
#   '''statement : expression
#                | expression statement
#                | statement expression
#                | statement NEWLINE'''
#   proc = p[1]
#   args = p[1:]
#   print('\nprocedure: ', proc)
#   print('arguments: ', args)
#   p[0] = [ p[:] ]

# # def p_procedure_call(p):
# #   '''statement : word '(' ')'
# #                | word '(' word ')'
# #                | word '(' statement ')'
# #                | statement '(' ')'
# #                | statement '(' word ')'
# #                | statement '(' statement ')'
# #                | statement NEWLINE'''
# #   proc = p[1]
# #   args = p[1:]
# #   print('\nprocedure: ', proc)
# #   print('arguments: ', args)
# #   p[0] = [ p[:] ]

#   # word -> single function i.e 'show()'
#   # word statement -> chain of words
  






# # def p_expression_set_var(p):
# #   '''statement : MAKE word_name word'''
# #   vars[p[3]] = p[4]
  
# # def p_expression_get_var(p):
# #   '''word : THING '"' WORD'''
# #   p[0] = vars[str(p[3])]


# # Print
# # def p_print(p):
# #   'statement : PRINT any_expression'
# #   print(str(p[2]))

# # Word expression ================================================

# # Word manipulators
# # def p_word_uppercase(p):
# #   'word : UPPERCASE word'
# #   p[0] = str(p[2]).upper()

# # def p_word_lowercase(p):
# #   'word : LOWERCASE word'
# #   p[0] = str(p[2]).lower()

# # def p_word_from_expression(p):
# #   'word : expression'
# #   p[0] = str(p[1])


# # Boolean Expression ===========================================

# # Logic operators
# # def p_bool_logical_and(p):
# #   'bool_expression : AND bool_expression bool_expression'
# #   p[0] = bool(p[1]) and bool(p[2])

# # def p_bool_logical_or(p):
# #   'bool_expression : OR bool_expression bool_expression'
# #   p[0] = bool(p[1]) or bool(p[2])

# # def p_bool_logical_not(p):
# #   'bool_expression : NOT bool_expression'
# #   p[0] = not bool(p[2])

# # def p_bool_expression_from_expression(p):
# #   'bool_expression : expression'
# #   p[0] = bool(p[1])


# # todo: temporary
# # def p_bool_expression_paren(p):
# #   '''bool_expression : bool_expression '[' bool_expression ']' '''
# #   if p[1]:
# #     p[0] = [3]

# # def p_bool_expression_to_bool(p):
# #   'bool_expression : TRUE'
# #   'TRUE : bool_expression'
# #   'bool_expression : FALSE'
# #   'FALSE : bool_expression'
# #   p[0] = p[1]

# # def p_dupa(p):
# #   '''dupa : '[' '"' ']' '''


# # Arithmetic Expression ========================================

# def p_arithmetic_expression_unary_operator(p):
#   '''word : '-' number %prec UMINUS'''
#   p[0] = -p[2]

# # Arithmetic comparison
# # def p_arithmetic_gt(p):
# #   'bool_expression : arithmetic_expression GT arithmetic_expression'
# #   p[0] = (p[1] > p[3])

# # def p_arithmetic_ge(p):
# #   'bool_expression : arithmetic_expression GE arithmetic_expression'
# #   p[0] = (p[1] >= p[3])

# # def p_arithmetic_lt(p):
# #   'bool_expression : arithmetic_expression LT arithmetic_expression'
# #   p[0] = (p[1] < p[3])

# # def p_arithmetic_le(p):
# #   'bool_expression : arithmetic_expression LE arithmetic_expression'
# #   p[0] = bool(p[1] <= p[3])

# # Arithmetic operators
# def p_arithmetic_binary_operator(p):
#   '''word : number '+' number
#           | number '-' number
#           | number '*' number
#           | number '/' number
#           | number '%' number
#           | number '^' number'''
#   p[0] = get_binary_operator_fn(p[2])(float(p[1]), float(p[3]))

# def p_arithmetic_binary_operator_v2(p):
#   '''word : ADD number number
#           | SUB number number
#           | MUL number number
#           | DIV number number
#           | MOD number number
#           | POW number number'''
#   p[0] = get_binary_operator_fn(p[1])(float(p[2]), float(p[3]))

# # def p_arithmetic_from_expression(p):
# #   'arithmetic_expression : expression'
# #   p[0] = float(p[1])

# # Expression ======================================================

# def p_expression_equal(p):
#   'word : word EQUAL word'
#   p[0] = ( p[1] == p[3] )

# def p_expression_not_equal(p):
#   'word : word NOT_EQUAL word'
#   p[0] = ( p[1] != p[3] )


# # def p_expression_number(p):
# #   'expression : arithmetic_expression'
# #   p[0] = float(p[1])
  
# # def p_expression_bool(p):
# #   'expression : bool_expression'
# #   p[0] = bool(p[1])
  
# # def p_expression_word(p):
# #   'expression : word'
# #   p[0] = str(p[1])

# def p_empty(p):
#   'empty :'
#   pass

# def p_error(p):
#   if p is not None:
#     print("Syntax Error:", p.__str__())

#screen.mainloop()