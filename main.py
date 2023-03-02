import socket
import sys
import threading
import datetime
import errno
import re
from flask import Flask

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connections = {}
idle_connections = {}
start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

handshaking = 0

server_address = ('localhost', 6626)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_address)
sock.settimeout(0.2)
sock.listen(1)

web_server = Flask(__name__)

def chat_server():
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
      except socket.timeout:
        print('timed out')
        continue
      except socket.error:
        print('disconnected')
        del connections[conn]
        continue
      while True:
        try:
          data = connections[conn][0].recv(16)
          received += data
        except:
          break
      if (received != bytes()):
        received = str(received, 'utf-8')
        if received[0] == "§":
          # is a command
          sender = re.search('§(.*?)>', received).group(1)
          command = re.search('§(.*?)>\[', received).group(1)
          match command:
            case "online_user":
              identifiers = re.search('§\[(.*)\]').group(1).split(",")
              results = []
              for id in identifiers:
                if id in connections:
                  results.append("online")
                elif id in idle_connections:
                  results.append("idle")
                else:
                  results.append("offline")
                connections[sender][0].sendall(bytes(','.join(results)), "utf-8")
            case "toggle_idle":
              print(connections)  
            case _:
              print("invalid command")
        elif received[0] == "@":
          # is a message
          sender = re.search('@(.*?)>', received).group(1)
          recipient = re.search('>(.*?)>\[', received).group(1)
          connections[recipient][0].sendall(bytes(received, encoding="utf-8"))

chat_server_thread = threading.Thread(target=chat_server)
chat_server_thread.start()

@web_server.route("/")
def index():
  return f"""
  <!DOCTYPE html>
  <html>
    <head>
      <title>Planck server status</title>
      <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
      <div id="conns-stats">
        <h1>Planck server status</h1>
        <img src="/static/images/online.png"> Connections: {len(connections)} <br>
        <img src="/static/images/idle.png"> Idlers: unknown <br>
      </div>
    <body>
  <html>
  """

web_server.run()