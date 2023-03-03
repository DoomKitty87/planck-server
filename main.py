import socket
import sys
import threading
import datetime
import errno
import re
import select
from flask import Flask

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connections = []
ids = []
statuses = []

online_ct = 0
idle_ct = 0
start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

server_address = ('localhost', 6626)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_address)
sock.settimeout(0.1)
sock.listen(1)

web_server = Flask(__name__)

def chat_server():
  while True:
    global online_ct, idle_ct, connections, ids, statuses
    print('Waiting for a connection')
    try:
      curr_client, curr_address = sock.accept()

      try:
        print(f"Connection from {curr_address}")

        key = ""

        try:
          curr_client.settimeout(0.1)
          data = curr_client.recv(256)
          key += str(data, 'utf-8')
          print(f'received {data}')
          connections.append(curr_client)
          ids.append(key)
          statuses.append("online")
          print(key)
          print(curr_client)
        except:
          print('handshake failed with ' + curr_address)
        
      finally:
        online_ct += 1
        print(f'finished initial client handshake with {curr_address}')

    except socket.timeout:
      pass
    
    if len(connections) == 0:
      continue
    r, w, e = select.select(connections, [], [], 0)

    if not r:
      print('No busy connections...')

    for conn in r:
      try:
        received = conn.recv(16)
      except socket.timeout:
        continue
      except ConnectionResetError:
        print('error occurred')
        conn.close()
        connections.remove(conn)
        statuses.remove(statuses[connections.index(conn)])
        ids.remove(ids[connections.index(conn)])
      while True:
        try:
          data = conn.recv(16)
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
                if statuses[ids.index(id)] == "online":
                  results.append("online")
                elif statuses[ids.index(id)] == "idle":
                  results.append("idle")
                else:
                  results.append("offline")
                conn.sendall(bytes(','.join(results)), "utf-8")
            case "toggle_idle":
              if statuses[connections.index(conn)] == "online":
                online_ct -= 1
                idle_ct += 1
                statuses[connections.index(conn)] = "idle"
              elif statuses[connections.index(conn)] == "idle":
                online_ct += 1
                idle_ct -= 1
                statuses[connections.index(conn)] = "online"
              else:
                print("toggle idle failed")
            case "client_hangup":
              connections.remove(conn)
              ids.remove(connections.index(conn))
              statuses.remove(connections.index(conn))
              break
            case _:
              print("invalid command")
        elif received[0] == "@":
          # is a message
          sender = re.search('@(.*?)>', received).group(1)
          recipient = re.search('>(.*?)>\[', received).group(1)
          connections[ids.index(recipient)].sendall(bytes(received, encoding="utf-8"))

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