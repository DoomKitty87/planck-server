import socket
import sys
import time

identifier = input("Input testing identifier: ")

def get_constants(prefix):
  return dict( (getattr(socket, n), n)
              for n in dir(socket)
              if n.startswith(prefix)
              )

families = get_constants('AF_')
types = get_constants('SOCK_')
protocols = get_constants('IPPROTO_')

sock = socket.create_connection(('localhost', 6626))

print ('Family  :' + families[sock.family])
print ('Type    :' + types[sock.type])
print ('Protocol:' + protocols[sock.proto])

try:
  message = bytes(identifier, encoding='utf8')
  print (f'sending {message}')
  sock.sendall(message)

finally:
    print ('handshake completed with server')
  
if (identifier == '22222'):
  time.sleep(3)
  message = bytes('Hello from client 2! It seems exciting over there.', encoding='utf-8')
  print("sending metadata")
  sock.sendall(bytes('12345', encoding='utf-8'))
  print("sending message body")
  sock.sendall(message)
  while True:
    pass
else:
  sock.setblocking(0)
  while True:
    received = bytes()
    while True:
      try:
        data = sock.recv(16)
        received += data
      except:
        if (len(received) > 0):
          print(str(received, 'utf-8'))
        break