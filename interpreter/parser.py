import inspect
from io import UnsupportedOperation
from re import DEBUG, I
import turtle
import ply.yacc as yacc
from interpreter.lexer import tokens
import copy
import time
from interpreter.logo import *

# This is what we want to parse
start = "word"

############################################################################################
# The procedure stack is never empty. There is at least one, 'Main' procedure
# at the bottom. It never returns any has has no limit in arguments it can take.
# In other words, it won't be ever called. This system is in ever lasting state of trying
# fill the list of required arguments. This is done on purpose to simplify logic and
# avoid hundreds of checks preventing out of the scope access of the procedure stack.
############################################################################################

stack = [{
    "argc": 9999999,
    "argv": ["Main"]
}]

# todo: does it make sense?
initial_stack_level = len(stack)

# Helpers


def NestedProcedureDoesNotReturnValue(procedure, outer_procedure):
    return SyntaxError(
        "Procedure ", procedure, " does not return any value, "
        "but ", outer_procedure, " requires some!"
    )


def WrongParameterCount(current, expected):
    return SyntaxError(
        "Wrong number of arguments! "
        "Gathered ", current, " parameters, "
        "but ", expected, " are required!"
    )


def TwoWordsNextToEachOtherAndNoneOfThemIsProcedure(left, right):
    return SyntaxError(
        "Two words next to each other and none of them is a procedure name!\n", left, " ", right
    )


def NoMoreWordsInThisLine(last_value):
    return SyntaxError(
        "Procedure ", last_value, " requires arguments, but this is end of the line!"
    )


def StackCorruption():
    return RuntimeError("Procedure stack is corrupted!\n", stack)


def call_procedure_wrapper(procedure, *args):
    try:
        return procedure(*args)
    except Exception as e:
        raise SyntaxError("Error during procedure call: ", e)


def does_procedure_return(func):
    lines, _ = inspect.getsourcelines(func)
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


def logo_sleep(duration):
    time.sleep(duration * 0.001)


def new_scope(prev_scope, args):
    s = copy.deepcopy(prev_scope)
    for k, v in args:
        s["variables"][k] = v
    return s


# Operators precedence
precedence = (
    ('nonassoc', 'MERGE_WORDS_AT_THE_END'),
    # ('nonassoc', 'NUM_TO_WORD'),
    ('right', '=', 'NOT_EQUAL'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', ':', '"'),
    ('left', '^'),
    # ('nonassoc', 'REDUCE_WORDS'), #, 'REDUCE_RETURN_WORDS'
    ('left', '(', ')'),  # , 'LPAREN', 'RPAREN'),
    # ('nonassoc', 'ALWAYS_REDUCE'),
)

# Internal interpreter state
scopes = []

scopes.append(new_scope({"variables": {}, "procedures": {}}, {}))
vars = (lambda: scopes[-1]["variables"])()
procedures = (lambda: scopes[-1]["procedures"])()


# Initialize turtle
screen = turtle.Screen()
screen.setup(width=800, height=640)
screen.title('Logo programming language interpreter')
turtle.mode("logo")
t = turtle.Turtle()


# Add some functions from the turtle library
# todo: lead them dynamically from the module
procedures["forward"] = lambda d: t.forward(d)
procedures["backward"] = lambda d: t.back(d)
procedures["right"] = lambda a: t.right(a)
procedures["left"] = lambda a: t.left(a)
procedures["show"] = lambda b: t.showturtle(b)
procedures["hide"] = lambda b: t.hideturtle(b)
procedures["setcolor"] = t.color
procedures["make"] = logo_make
procedures["thing"] = logo_thing
procedures["print"] = logo_print
procedures["sleep"] = logo_sleep
procedures["get_666"] = lambda: 20


def handle_word(word):
    # First we must decide what kind of word we are dealing with.

    # None is a special case, we just ignore it.
    if word is None:
        return

    if word in procedures:
        return handle_procedure(word)
    else:
        return handle_value(word)


############################################################################################
# When the word is a procedure name, then:
#   1. Get procedure's argument count and check whether it is expected to return a value.
#   2. When a procedure does not return any value and the procedure stack is at
#       the same level as it was before beginning of this line - report syntax error. <----------- reconsider this & do only at the line end
#   3. When a procedure takes no arguments then call it right away,
#       and if possible, add its result to the outer procedure's argument list.
#   4. Otherwise put currently handled procedure on the procedure stack and quit.
############################################################################################
def handle_procedure(procedure_name):

    procedure = procedures[procedure_name]

    # 1. Gather information about procedure
    required_argc = len(inspect.getfullargspec(procedure).args)
    does_return = does_procedure_return(procedure)

    # 2. Check syntax
    if len(stack) > initial_stack_level and not does_return:
        raise NestedProcedureDoesNotReturnValue(
            procedure_name, get_current_proc_name())

    # 3. When procedure takes no args then call it and handle its value
    if required_argc == 0:
        result = call_procedure_wrapper(procedure)
        if does_return:
            return handle_value(result)
    else:

        # 4. Put procedure on the stack
        stack.append({
            "argc": required_argc,
            "argv": [procedure_name]
        })

    # 5. Returno procedure name
    # return procedure_name

    # Append result to the list of parameters of the outer procedure
    # But only if there are no parenthesis between them.
    # Count and compare open and closed parenthesis for current lexer position
    # current_lexer_pos = p.lexer.lexpos
    # opened_parenthesis = sum(
    #     1 for i in p.lexer.p["open"] if i < current_lexer_pos)
    # closed_parenthesis = sum(
    #     1 for i in p.lexer.p["close"] if i < current_lexer_pos)

    # print("opened: ", opened_parenthesis)
    # print("closed: ", closed_parenthesis)

    # if opened_parenthesis == closed_parenthesis:
    #     outer_procedure.append(result)
    #     return

    # # Always try to return value as an int, because it is easly convertible to word
    # # reconsider this sentence /\/\/\
    # if does_return:
    #     try:
    #         return int(result)
    #     except:
    #         return result


#############################################################################################


def get_current_proc_name():
    return stack[-1]["argv"][0]


def procedure_on_stack_may_be_called():
    return len(stack) > 1 and len(stack[-1]["argv"]) == stack[-1]["argc"] + 1


############################################################################################
# Of the provided word is not a procedure then it must be regular string or number.
# It can't be a variable name, because we resolve them immediately, using operator '"'.
#   1. First, add an argument to the procedure list at the very top of the stack.
#   2. When number of arguments on list equals required count, then:
#     a) Pop the procedure from the top of the stack.
#     b) Confirm that procedure argument count matches the one of procedure.
#     c) Verify, whether syntax might be broken checkin if procedure returns.
#     d) Call the procedure and if possible add it's result to the next
#       procedure on the stack.
#     e) Go back to point 2.
############################################################################################
def handle_value(value):

    # 0. When no function is on stack (except the main) just return it's value
    if len(stack) == 1:
        return value

    # 1. Add argument to the very top procedure on the stack.
    stack[-1]["argv"].append(value)

    print("New value on ", get_current_proc_name(), " argument list: ", value)

    # 2. Check in the loop whether most top procedure can be executed
    #    We must check 'top_argc + 1' beacuase there is also a procedure
    #    name on the list.
    result = None
    while procedure_on_stack_may_be_called():

        # a) Take procedude data from the stack and load real procedure
        #    based on that.
        proc = stack.pop()
        argv = proc["argv"]
        argc = proc["argc"]
        procedure_name = argv.pop(0)
        procedure = procedures[procedure_name]

        print("Start calling procedure: ", get_current_proc_name(),
              " with arguments: ", argv)

        print("Stack after popping most top procedure: ", stack)

        # b) Check number of arguments, just in case
        expected_argc = len(inspect.getfullargspec(procedure).args)

        print("Number of expected arguments: ",
              expected_argc, "delivered: ", argc)

        if argc != expected_argc:
            raise WrongParameterCount(argc, expected_argc)

        # c) Check whether procedure returns and whether it can be called
        #    on this stack level.
        does_return = does_procedure_return(procedure)

        print("Procedure ", procedure_name, " returns? ", does_return)

        # we will have to fix this 1 for nested procedure definitions
        if len(stack) > 1 and not does_return:
            raise NestedProcedureDoesNotReturnValue(
                procedure_name, get_current_proc_name())

        # d) Call the procedure and if it's possible put it's result on the
        #    list on top of the stack. We must also verify if we are between
        #    parentheses.
        result = call_procedure_wrapper(procedure, *argv)

        if does_return:
            stack[-1]["argv"].append(result)

    # Return the value of last called procedure
    return result

    # Append result to the list of parameters of the outer procedure
    # But only if there are no parenthesis between them.
    # Count and compare open and closed parenthesis for current lexer position

    # current_lexer_pos = p.lexer.lexpos

    # opened_parenthesis = sum(
    #     1 for i in p.lexer.p["open"] if i < current_lexer_pos)
    # closed_parenthesis = sum(
    #     1 for i in p.lexer.p["close"] if i < current_lexer_pos)

    # print("opened: ", opened_parenthesis)
    # print("closed: ", closed_parenthesis)

    # if opened_parenthesis == closed_parenthesis:
    #     outer_procedure.append(result)
    #     return

    # todo: check whether it will help? Next call
    # to this function will deal with this and it
    # will solve problem with fn ()
    # if does_return:
    #     try:
    #         return int(result)
    #     except:
    #         return result


#########################################################################################
# This should be possible only when any of the two is None or one is existing procedure
# call. Although it shouldn't happen now. #todo: confirm that and raise an Exception in
# case any word is None.
#########################################################################################
def handle_word_word(left_word, right_word):
    # In case any of these words is None just return the opposite
    if left_word is None:
        return right_word
    elif right_word is None:
        return left_word

    # When the left word is a procedure name then handle right word
    if left_word in procedures:
        # todo: what if we have proc1 proc2 proc3 proc4 ?!
        return handle_word(right_word)
    else:
        raise TwoWordsNextToEachOtherAndNoneOfThemIsProcedure(
            left_word, right_word)


#########################################################################################
# New line is kind of special. IT requires to take all procedures from the stack and
# call them. In case of missing variables dnagling words we just raise an exception.
#########################################################################################
def handle_new_line(last_in_line):

    # this should always return the value, not a procedure name
    # the reason why is that if last_in_line would be a procedure name
    # it should be called with no arguments and its value should be returned here
    last_value_in_line = handle_word(last_in_line)

    # we should check it anyway
    if last_value_in_line in procedures:
        raise NoMoreWordsInThisLine(last_value_in_line)

    # If last_in_line was a value then handle_value should take out
    # all procedures from the stack and call them.
    # In case it was a procedure name we either failed above or get the return value
    return handle_value(last_value_in_line)


# todo: move this to documentation
#########################################################################################
# Below are all of the parser's rules used in this project.
# We have tried many approaches to write this interpreter. Few of them even worked
# to some degree. However, after spending so many hours trying to write,
# not the best, but only a decent interpreter of LOGO. After, I don't even know which
# trial and starting from scratch. We finally figured it out!
# Here is how you can make simple, but supprisingly flexible interpreter of LOGO.
# First of all, in LOGO, everything may be treated as a word. Starting from
# procedure's name and the way you call it, to the variable's name and value, to the
# numbers, strings and everything else. This is actually the biggest obstacle
# to properly interpret LOGO. You see, in LOGO, at least in dialect we have studied,
# you may write all of the code in one line. At least, as long as it makes logical
# sense and allows for calling all nested procedures with required number
# of arguments. So, just imagine that this text is just very long chain of nested
# functions, variable's names and strings. Just kidding, it's not that bad. I mean...
# It is, but by introducing few additional restrictions it's possible to do it well.
# In our parser we have tried to use in our advantage ambiguyity of the language
# structure. Our interpreter splits the input to words and then, by using few simple
# converters, casts everything to words. For example strings, represented by pure
# text with just one quotation mark at the beginning must be converted to words
# in the very moment our very simple lexer gives us a new token, which I guess we
# can start calling word. The same with all the variables, to be compliant with
# the standard, we must replace this form of variable ':variable' with it's value.
# Which, by the way, may be the name of another variable. Or procedure, who knows?
#########################################################################################

def p_work_newline(p):
    'word : word NEWLINE'
    'word : word NEWLINE NEWLINE'
    p[0] = handle_new_line(p[1])


# def p_end_of_line(p):
#     '''word : word NEWLINE
#        word : number NEWLINE'''  # %prec ALWAYS_REDUCE'''
#     p[0] = p[1]


# def p_end_eat_result(p):
#     '''word   : line_result word
#        word   : NEWLINE word'''  # %prec ALWAYS_REDUCE'''
#     #  number : line_result number %prec ALWAYS_REDUCE
#     #  number : NEWLINE number %prec ALWAYS_REDUCE'''
#     p[0] = p[2]


def get_binary_operator_fn(op):
    if op == '+':
        return lambda x, y: x+y
    elif op == '-':
        return lambda x, y: x-y
    elif op == '*':
        return lambda x, y: x*y
    elif op == '/':
        return lambda x, y: x/y
    elif op == '%':
        return lambda x, y: x % y
    elif op == '^':
        return lambda x, y: pow(x, y)
    else:
        raise UnsupportedOperation(f"Unknown operator: {op}")


def p_number(p):
    'number : NUMBER'
    p[0] = p[1]  # todo: make sure  arithmetic is handled first


# def p_number_in_parents(p):
#     '''number : '(' number ')' '''
#     p[0] = p[2]

# def p_word_numer_bianry_operator_parenthesis_upgrade(p):
#   '''number : '(' word '+' number ')'
#             | '(' word '-' number ')'
#             | '(' word '*' number ')'
#             | '(' word '/' number ')'
#             | '(' word '%' number ')'
#             | '(' word '^' number ')'
#             | '(' number '*' word ')'
#             | '(' number '/' word ')'
#             | '(' number '%' word ')'
#             | '(' number '^' word ')' '''
#   p[0] = int(get_binary_operator_fn(p[2])(int(p[2]), int(p[4])))


# def p_arithmetic_binary_operator_numbers(p):
#   '''number : number '+' number
#             | number '-' number
#             | number '*' number
#             | number '/' number
#             | number '%' number
#             | number '^' number
#             | '(' number '+' number ')'
#             | '(' number '-' number ')'
#             | '(' number '*' number ')'
#             | '(' number '/' number ')'
#             | '(' number '%' number ')'
#             | '(' number '^' number ')' '''
#   p[0] = int(get_binary_operator_fn(p[2])(int(p[1]), int(p[3])))

def p_arithmetic_binary_operator(p):
    '''word : word '+' word
            | word '-' word
            | word '*' word
            | word '/' word
            | word '%' word
            | word '^' word'''
    print(p[1], p[2], p[3])
    operator_fn = get_binary_operator_fn(p[2])
    if isinstance(p[1], float) and isinstance(p[3], float):
        p[0] = float(operator_fn(p[1], p[3]))
    else:
        p[0] = handle_word(operator_fn(p[1], p[3]))


def p_word_equals_word(p):
    '''word : word '=' word'''
    p[0] = bool(p[1] == p[3])


def p_word_not_equal(p):
    'word : word NOT_EQUAL word'
    p[0] = bool(p[1] != p[3])


# As you can see above, we have the same operations for strings and numbers.
# This is because we relay on Python's dynamic typing system.
# If operations is not possible, what else can we do?

###############################################################################

# Cast everything to Word

# A word may be:
#  * The outcome of a procedure call with any number of arguments
#  * A number or a math equation (ofc reduced, by this parser to just one number)
#  * A variable's value or variable's name or just a string

def p_word_in_parentheses(p):
    '''word : '(' word ')' '''
    p[0] = handle_word(p[2])


def p_word(p):
    'word : WORD'
    p[0] = handle_word(p[1])  # todo: what about the second arg


def p_word_number(p):
    'word : number'  # %prec NUM_TO_WORD'
    p[0] = handle_word(float(p[1]))


def p_word_value(p):
    '''word : ':' WORD'''
    p[0] = handle_word(vars[p[2]])


def p_word_name(p):
    '''word : '"' WORD'''
    p[0] = handle_word(p[2])


def p_word_word(p):
    'word : word word %prec MERGE_WORDS_AT_THE_END'
    p[0] = handle_word_word(p[1], p[2])

############################################################################


# # When at the end of the line we are still inside a function which begins in this line, then
# # this is a syntax error.
# def p_end_of_line(p):
#   'word : NEWLINE word'
#   'word : word NEWLINE word'
#   'word : word NEWLINE'
#   if len(stack) != initial_stack_level:
#     proc = stack[-1]
#     proc_name = proc["argv"].pop(0)
#     no_missing_args = proc["argc"] - len(proc["argv"])
#     raise SyntaxError("A procedure[", proc_name, "] call  must end on the same line it started on (missing arguments: ", no_missing_args, ")")
#   else:
#     initial_stack_level = len(stack)
#     p[0] = handle_word(p[-1])

# def p_return_word_newline(p):
#   'return_word : word NEWLINE %prec REDUCE_RETURN_WORDS'
#   p[0] = p[1]

# def p_return_word_reduce(p):
#   'return_word : return_word return_word %prec REDUCE_RETURN_WORDS'
#   'return_word : return_word NEWLINE %prec REDUCE_RETURN_WORDS'
#   p[0] = p[1]


###########################################################
# I'm not sure if we even use these

def p_empty(p):
    'empty :'
    pass


def p_error(p):
    if p is not None:
        print("Syntax Error:", p.__str__())


def new_parser():
    return yacc.yacc(debug=True)


parser = yacc.yacc(debug=True)


def run_parser(input):
    parser.parse(input, debug=True, tracking=True)
