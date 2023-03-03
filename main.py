import socket
import sys
import threading
import datetime
import errno
import re
from flask import Flask

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connections = {}
online_ct = 0
idle_ct = 0
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
    global online_ct, idle_ct
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
          connections.update({key:[curr_client, curr_address, "online"]})
          print(key)
          print(connections[key])
        except:
          print('handshake failed with ' + curr_address[0])
        
      finally:
        online_ct += 1
        print(f'finished initial client handshake with {curr_address[0]}')

    except socket.timeout:
      pass

    for conn in connections:
      try:
        received = connections[conn][0].recv(16)
        if (received == bytes()):
          del connections[conn]
          break
      except socket.EWOULDBLOCK or socket.EAGAIN:
        print('timed out')
        continue
      except socket.error:
        print('disconnected')
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
          command = re.search('>(.*?)>\[', received).group(1)
          match command:
            case "online_user":
              identifiers = re.search('§\[(.*)\]').group(1).split(",")
              results = []
              for id in identifiers:
                if id in connections[id][2] == "online":
                  results.append("online")
                elif id in connections[id][2] == "idle":
                  results.append("idle")
                else:
                  results.append("offline")
                connections[sender][0].sendall(bytes(','.join(results)), "utf-8")
            case "toggle_idle":
              if connections[sender][2] == "online":
                online_ct -= 1
                idle_ct += 1
                connections[sender][2] = "idle"
              elif connections[sender][2] == "idle":
                online_ct += 1
                idle_ct -= 1
                connections[sender][2] = "online"
              else:
                print("toggle idle failed")
            case "client_hangup":
              del connections[sender]
              break
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
        <img src="/static/images/online.png"> Online users: {online_ct} <br>
        <img src="/static/images/idle.png"> Idle users: {idle_ct} <br>
      </div>
    <body>
  <html>
  """

web_server.run()