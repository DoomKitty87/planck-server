import socket
import sys
import threading
import datetime
import errno
import re
import select
from flask import Flask
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QGridLayout, QPushButton, QListView
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QIcon, QStandardItem, QStandardItemModel

appInstance = QApplication(sys.argv)

window = QWidget()
window.setGeometry(400, 400, 800, 400)
window.setWindowTitle('Planck Server Alpha')

with open("styles.css", "r") as f:
    window.setStyleSheet(f.read())

layout = QGridLayout()

port_select = QLineEdit()
set_address_button = QPushButton("Assign server port")
port_label = QLabel("Enter server port (defaults to 6626)")
start_server_button = QPushButton("Start chat server")
stop_server_button = QPushButton("Stop chat server")

layout.addWidget(port_label, 0, 0)
layout.addWidget(port_select, 1, 0)
layout.addWidget(set_address_button, 2, 0)
layout.addWidget(start_server_button, 3, 0)
layout.addWidget(stop_server_button, 4, 0)

window.setLayout(layout)

server_address = ('localhost', 6626)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_address)
sock.settimeout(0.1)
sock.listen(1)

connections = []
ids = []
statuses = []

online_ct = 0
idle_ct = 0
start_time = 0

running = False

def run_chatserver():
  global online_ct, idle_ct, connections, ids, statuses, running
  while True:
    if not running: break
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
        if statuses[connections.index(conn)] == "online":
          online_ct -= 1
        elif statuses[connections.index(conn)] == "idle":
          idle_ct -= 1
        conn.close()
        statuses.remove(statuses[connections.index(conn)])
        ids.remove(ids[connections.index(conn)])
        connections.remove(conn)
      except:
        print('error occurred')
        if statuses[connections.index(conn)] == "online":
          online_ct -= 1
        elif statuses[connections.index(conn)] == "idle":
          idle_ct -= 1
        conn.close()
        statuses.remove(statuses[connections.index(conn)])
        ids.remove(ids[connections.index(conn)])
        connections.remove(conn)
      while True:
        try:
          data = conn.recv(16)
          received += data
          if (data == bytes()): break
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
              if statuses[connections.index(conn)] == "online":
                online_ct -= 1
              elif statuses[connections.index(conn)] == "idle":
                idle_ct -= 1
              conn.close()
              statuses.remove(statuses[connections.index(conn)])
              ids.remove(ids[connections.index(conn)])
              connections.remove(conn)
              break
            case _:
              print("invalid command")
        elif received[0] == "@":
          # is a message
          sender = re.search('@(.*?)>', received).group(1)
          recipient = re.search('>(.*?)>\[', received).group(1)
          connections[ids.index(recipient)].sendall(bytes(received, encoding="utf-8"))

chat_server_thread = threading.Thread(target=run_chatserver)

def start_server():
  global start_time, running
  if running: return
  start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  running = True
  chat_server_thread.start()

def stop_server():
  global running
  if not running: return
  sock.listen(0)
  running = False
  chat_server_thread = threading.Thread(target=run_chatserver)

def set_server_address():
  global server_address
  if (('localhost', port_select.text()) != server_address):
    server_address = ('localhost', int(port_select.text()))
    sock.bind(server_address)

set_address_button.clicked.connect(set_server_address)
start_server_button.clicked.connect(start_server)
stop_server_button.clicked.connect(stop_server)

web_server = Flask(__name__)

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

#web_server_thread = threading.Thread(target=web_server.run)
#web_server_thread.start()

def on_exit():
  global running
  running = False

appInstance.aboutToQuit.connect(on_exit)

print("opening gui")
window.show()
sys.exit(appInstance.exec_())
