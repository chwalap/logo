from interpreter.lparser import run_parser

with open('demo.trtl') as f:
    contents = f.read()

run_parser(contents)
