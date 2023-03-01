import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connections = {}

handshaking = 0

server_address = ('localhost', 6626)
sock.bind(server_address)
sock.settimeout(0.2)
sock.listen(1)


while True:
  print('Waiting for a connection')
  try:
    curr_client, curr_address = sock.accept()

    try:
      print(f"Connection from {curr_address}")
      curr_client.settimeout(0.2)

      key = ""

      try:
        data = curr_client.recv(256)
        key += str(data, 'utf-8')
        print(f'received {data}')
        connections.update({key:(curr_client, curr_address)})
        print(key)
        print(connections[key])
      except:
        print('handshake failed with ' + curr_address[0])
      
    finally:
      print(f'finished initial client handshake with {curr_address[0]}')

  except socket.timeout:
    pass

  for conn in connections:
    try:
      received = connections[conn][0].recv(16)
    except:
      continue
    while True:
      try:
        data = connections[conn][0].recv(16)
        received += data
        print(received)
      except:
        break
    if (received != ""):
      received = str(received, 'utf-8')
      identifier = received[:5]
      print(identifier)
      if (len(identifier) > 0):
        connections[identifier][0].sendall(bytes(received[5:], encoding="utf-8"))