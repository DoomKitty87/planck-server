import sys
import socket
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QVBoxLayout, QPushButton, QPlainTextEdit
from PySide2.QtCore import QTimer

appInstance = QApplication(sys.argv)

window = QWidget()
window.setGeometry(100, 100, 250, 150)
window.setWindowTitle('Planck Client Alpha')

label1 = QLabel('Enter host: ')
label2 = QLabel('Enter id: ')

label3 = QLabel('Enter recipient id: ')
label4 = QLabel('Enter message: ')

hostentry = QLineEdit()
identity = QLineEdit()
toidentry = QLineEdit()
messageentry = QPlainTextEdit()

connectbutton = QPushButton('connect to server')

sendmessagebutton = QPushButton('Send Message')

layout = QVBoxLayout()
layout.addWidget(label1)
layout.addWidget(hostentry)
layout.addWidget(label2)
layout.addWidget(identity)
layout.addWidget(connectbutton)
layout.addWidget(label3)
layout.addWidget(toidentry)
layout.addWidget(label4)
layout.addWidget(messageentry)
layout.addWidget(sendmessagebutton)

window.setLayout(layout)

connected = False
sock = None

def wait_for_messages():
  if (connected == True):
    received = bytes()
    while True:
      try:
        data = sock.recv(16)
        received += data
      except:
        if (len(received) > 0):
          print(str(received, 'utf-8'))
        break

def connect_to_server():
  try:
    sock = socket.create_connection((hostentry.text(), 6626))
    sock.setblocking(0)
    message = bytes(identity.text(), encoding='utf8')
    print(f'sending {message}')
    sock.sendall(message)
    connected = True
    return sock

  finally:
    print('handshake completed with server')

def send_message():
  if (connected == False):
    print('not connected to server.')
    return
  recipient = toidentry.text()
  message = messageentry.text()
  print('sending message...')
  print(f'message contents: {message}')
  print(f'to {recipient} on server {hostentry.text()}')
  sock.sendall(bytes(recipient, encoding='utf-8'))
  sock.sendall(bytes(message, encoding='utf-8'))

timer = QTimer()
timer.timeout.connect(wait_for_messages)
timer.setInterval(500)

connectbutton.clicked.connect(connect_to_server)
sendmessagebutton.clicked.connect(send_message)

timer.start()
window.show()

sys.exit(appInstance.exec_())