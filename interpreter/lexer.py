import re
import ply.lex as lex

# states = (
#    ('tocode','inclusive'),
#    ('toargs', 'exclusive'),
# )

literals = ['+', '-', '*', '/', '%', '=',
            ')', '(', '[', ']', '>', '<', ':', '"']

tokens = [
    # 'TRUE', 'FALSE',
    # 'EQUAL', 'NOT_EQUAL',
    # 'GT', 'GE', 'LT', 'LE',
    # 'AND', 'OR', 'NOT',

    'NOT_EQUAL',

    'NUMBER',
    # 'ADD', 'SUB',
    # 'MUL', 'DIV',
    # 'MOD', 'POW',

    # 'IF', 'IFELSE',

    'REPEAT',

    'WORD',  # 'QUOTED_WORD',
    # 'MAKE', 'THING',

    # 'PRINT',
    # 'UPPERCASE', 'LOWERCASE',

    # 'TO', 'TO_NAME', 'TO_ARG', 'TO_CODE', #'END',

    'NEWLINE',
    # 'LPAREN', 'RPAREN',
]

#t_QUOTED_WORD = r'''(?i)[\"\'](?:[\w]|\\\ )*'''


def t_REPEAT(t):
    r'REPEAT'
    return t


def t_NUMBER(t):
    r'[+-]?([0-9]*[.])?[0-9]+'
    t.value = float(t.value)
    return t


def t_WORD(t):
    r'\w(?:[\w]|\\\ )*'  # [a-zA-Z][\w_]*'
    t.value = t.value.replace("\\ ", " ")
    return t


# def t_LPAREN(t):
#     r'\('
#     t.lexer.p["open"].append(t.lexer.lexpos)
#     return t


# def t_RPAREN(t):
#     r'\)'
#     t.lexer.p["close"].append(t.lexer.lexpos)
#     return t


def t_NOT_EQUAL(t):
    r'<>'
    return t


# t_toargs_TO_ARG = r'\:[a-zA-Z][\w+_]*'
# t_toargs_TO_NAME = r'[a-zA-Z][\w+_]*'

# def t_TO(t):
#   r'(?i)to'
#   t.lexer.push_state('toargs')
#   return t

# def t_toargs_NEWLINE(t):
#   r'\n+'
#   t.lexer.pop_state() # toargs
#   t.lexer.push_state('tocode')
#   t.lexer.code_start = t.lexer.lexpos
#   return t

# def t_toargs_error(t):
#   print("[TO_ARGS] Illegal character '%s' at:" % t.value[0], t.lineno)

# t_toargs_ignore = ' \t'

# def t_tocode_END(t):
#   r'(?i)end'
#   t.value = t.lexer.lexdata[t.lexer.code_start : t.lexer.lexpos + 1]
#   t.type = "TO_CODE"
#   t.lexer.lineno += t.value.count('\n')
#   t.lexer.pop_state() # tocode
#   return t


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.value = t.value[:1]
    return t


t_ignore = ' \t'
t_ignore_COMMENT = r';.*'


def t_error(t):
    print("Illegal character '%s' at:" % t.value[0], t.lineno)


def t_eof(t):
    return None


lexer = lex.lex()  # debug=True, reflags=re.VERBOSE)
# additional struct for storing parenthesis positions
lexer.p = {"open": [], "close": []}
