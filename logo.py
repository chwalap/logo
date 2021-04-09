from interpreter.lexer import lexer
from view.init import init_turtle, loop
from view.turtle import create_turtle

with open('demo.trtl') as f:
    contents = f.read()

lexer.input(contents)

init_turtle()

t = create_turtle()

while True:
  tok = lexer.token()
  if not tok: 
    break

  print(tok)

  if tok.type == 'FORWARD':
    value = lexer.token()
    if not value:
      break

    t.forward(value.value)
  
  elif tok.type == 'BACKWARD':
    value = lexer.token()
    if not value:
      break

    t.backward(value.value)
  
  elif tok.type == 'RIGHT':
    value = lexer.token()
    if not value:
      break

    t.right(value.value)
  
  elif tok.type == 'LEFT':
    value = lexer.token()
    if not value:
      break

    t.left(value.value)

  else:
    print('Dupa')

loop()