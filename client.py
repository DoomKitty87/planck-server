import sys
import socket
import re
import rsa
from datetime import datetime
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QGridLayout, QPushButton, QPlainTextEdit, QListView
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QIcon, QStandardItem, QStandardItemModel

appInstance = QApplication(sys.argv)

window = QWidget()
window.setGeometry(400, 400, 600, 400)
window.setWindowTitle('Planck Client Alpha')

with open("styles.css", "r") as f:
  window.setStyleSheet(f.read())

connectedlabel = QLabel("OFFLINE")
connlightbutton = QPushButton()
connlightbutton.setFixedWidth(24)
connlightbutton.setFixedHeight(24)
connlightbutton.setStyleSheet("QPushButton { border : 0; background: transparent; }")
connlightbutton.setIcon(QIcon("static/images/idle.png"))
connlightbutton.setIconSize(QSize(24, 24))
currconnectionlabel = QLabel("NO SERVER")

label1 = QLabel('SERVER HOST')
label1b = QLabel('SERVER PORT')
label2 = QLabel('RSA PUB KEY')

label3 = QLabel('RECIPIENT')
label4 = QLabel('MESSAGE')

hostentry = QLineEdit()
portentry = QLineEdit()
identity = QLineEdit()
toidentry = QLineEdit()
messageentry = QPlainTextEdit()

connectbutton = QPushButton('CONNECT')
disconnectbutton = QPushButton('DISCONNECT')
newkeybutton = QPushButton('NEW KEYS')

sendmessagebutton = QPushButton('SEND MESSAGE')
#messageInfo = QLabel('')
#messageDisplay = QLabel('')
messageBox = QListView()
model = QStandardItemModel()
messageBox.setModel(model)

label5 = QLabel('RSA PRIV KEY')
privatekey = QLineEdit()

layout = QGridLayout()
layout.addWidget(connlightbutton, 0, 0, 1, 1)
layout.addWidget(connectedlabel, 0, 1, 1, 1)
layout.addWidget(currconnectionlabel, 1, 1, 1, 1)
layout.addWidget(label1, 2, 1)
layout.addWidget(hostentry, 3, 1)
layout.addWidget(label1b, 4, 1)
layout.addWidget(portentry, 5, 1)
layout.addWidget(label2, 6, 1)
layout.addWidget(identity, 7, 1)
layout.addWidget(label5, 8, 1)
layout.addWidget(privatekey, 9, 1)
layout.addWidget(connectbutton, 10, 1)
layout.addWidget(disconnectbutton, 11, 1)
layout.addWidget(newkeybutton, 12, 1)
layout.addWidget(label3, 14, 2)
layout.addWidget(toidentry, 14, 3)
layout.addWidget(label4, 15, 2)
layout.addWidget(messageentry, 15, 3)
layout.addWidget(sendmessagebutton, 16, 3)
layout.addWidget(messageBox, 0, 2, 13, 2)

window.setLayout(layout)

connected = False
sock = None
identifier = None
privkey = None
pubkey = None

def wait_for_messages():
  global connected
  if (connected == True):
    received = bytes()
    while True:
      try:
        data = sock.recv(16)
        received += data
      except:
        if (len(received) > 0):
          # Recieved a message
          # print(str(received, 'utf-8'))
          message = rsa.decrypt(received.split(b'>[]')[1], privkey).decode()
          disp = QStandardItem(f"Message from {re.search('-----BEGIN RSA PUBLIC KEY-----(.*?)-----END RSA PUBLIC KEY-----', str(received.split(b'>[]')[0], 'utf-8'), re.DOTALL).group(1)} at {datetime.now().strftime('%H:%M:%S')}:\n{message}")
          model.appendRow(disp)
          messageBox.scrollToBottom()
        break

def toggle_connect_to_server():
  global connected
  global sock
  global connectedlabel
  global connlightbutton
  global identifier
  if connected == False:
    sock = socket.create_connection((hostentry.text(), portentry.text()))
    sock.setblocking(0)
    message = bytes(identity.text(), encoding='utf8')
    print(f'sending {message}')
    sock.sendall(message)
    connected = True
    currconnectionlabel.setText(hostentry.text() + ":" + portentry.text())
  else:
    sock.sendall(bytes(f"§{identifier}>client_hangup>[]", encoding='utf-8'))
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    sock = socket.create_connection((hostentry.text(), portentry.text()))
    sock.setblocking(0)
    message = bytes(identity.text(), encoding='utf8')
    print(f'sending {message}')
    sock.sendall(message)
    connected = True
    currconnectionlabel.setText(hostentry.text() + ":" + portentry.text())
  connectedlabel.setText("Online.")
  connlightbutton.setIcon(QIcon("static/images/online.png"))
  identifier = identity.text()
  print('handshake completed with server')

def disconnect_from_server():
  global connected
  global sock
  global connectedlabel
  global connlightbutton
  if (connected == True):
    sock.sendall(bytes(f"§{identifier}>client_hangup>[]", encoding='utf-8'))
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    connected = False
    currconnectionlabel.setText("No server connected.")
    connectedlabel.setText("Offline.")
    connlightbutton.setIcon(QIcon("static/images/idle.png"))

def send_message():
  global sock
  global connected
  if (connected == False):
    print('not connected to server.')
    return
  recipient = toidentry.text()
  message = messageentry.toPlainText()
  print('sending message...')
  print(f'message contents: {message}')
  print(f'to {recipient} on server {hostentry.text()}')
  sock.sendall(bytes(f"@{identifier}>{toidentry.text()}>[]", encoding='utf-8') + rsa.encrypt(messageentry.toPlainText().encode(), rsa.PublicKey.load_pkcs1(toidentry.text().encode())))
  messageentry.clear()

def toggle_idle():
  sock.sendall(bytes(f"§{identifier}>toggle_idle>[]", encoding='utf-8'))

def generate_rsa():
  global pubkey, privkey
  newpublic, newprivate = rsa.newkeys(512)
  identity.setText(newpublic.save_pkcs1().decode())
  privatekey.setText(newprivate.save_pkcs1().decode())
  pubkey = newpublic
  privkey = newprivate

def on_exit():
  print('exiting')

timer = QTimer()
timer.timeout.connect(wait_for_messages)
timer.setInterval(500)

connectbutton.clicked.connect(toggle_connect_to_server)
disconnectbutton.clicked.connect(disconnect_from_server)
sendmessagebutton.clicked.connect(send_message)
connlightbutton.clicked.connect(toggle_idle)
newkeybutton.clicked.connect(generate_rsa)
appInstance.aboutToQuit.connect(on_exit)

timer.start()
window.show()

sys.exit(appInstance.exec_())
