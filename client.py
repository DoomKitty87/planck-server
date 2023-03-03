import sys
import socket
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QGridLayout, QPushButton, QPlainTextEdit
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QIcon

appInstance = QApplication(sys.argv)

window = QWidget()
window.setGeometry(100, 100, 250, 150)
window.setWindowTitle('Planck Client Alpha')

connectedlabel = QLabel("Offline.")
connlightbutton = QPushButton()
connlightbutton.setFixedWidth(24)
connlightbutton.setFixedHeight(24)
connlightbutton.setIcon(QIcon("C:/Users/SpikyLlama/Documents/GitHub/planck-server/static/images/idle.png"))
connlightbutton.setIconSize(QSize(24, 24))
currconnectionlabel = QLabel("No server connected.")

label1 = QLabel('Enter host and port: ')
label2 = QLabel('Enter id: ')

label3 = QLabel('Enter recipient id: ')
label4 = QLabel('Enter message: ')

hostentry = QLineEdit()
portentry = QLineEdit()
identity = QLineEdit()
toidentry = QLineEdit()
messageentry = QPlainTextEdit()

connectbutton = QPushButton('connect to server')

sendmessagebutton = QPushButton('send message')

toggleidlebutton = QPushButton('toggle idle')

layout = QGridLayout()
layout.addWidget(connlightbutton, 0, 0, 1, 1)
layout.addWidget(connectedlabel, 0, 1, 1, 1)
layout.addWidget(currconnectionlabel, 1, 1, 1, 1)
layout.addWidget(label1)
layout.addWidget(hostentry)
layout.addWidget(portentry)
layout.addWidget(label2)
layout.addWidget(identity)
layout.addWidget(connectbutton)
layout.addWidget(label3)
layout.addWidget(toidentry)
layout.addWidget(label4)
layout.addWidget(messageentry)
layout.addWidget(sendmessagebutton)
layout.addWidget(toggleidlebutton)

window.setLayout(layout)

connected = False
sock = None

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
          print(str(received, 'utf-8'))
        break

def toggle_connect_to_server():
  global connected
  global sock
  if sock == None:
    sock = socket.create_connection((hostentry.text(), portentry.text()))
    sock.setblocking(0)
    message = bytes(identity.text(), encoding='utf8')
    print(f'sending {message}')
    sock.sendall(message)
    connected = True
    currconnectionlabel.setText(hostentry.text() + ":" + portentry.text())
  else:
    sock.close()
    sock = socket.create_connection((hostentry.text(), portentry.text()))
    sock.setblocking(0)
    message = bytes(identity.text(), encoding='utf8')
    print(f'sending {message}')
    sock.sendall(message)
    connected = True
    currconnectionlabel.setText(hostentry.text() + ":" + portentry.text())
  connectedlabel = "Online."
  print('handshake completed with server')

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
  sock.sendall(bytes(f"@{identity.text()}>{toidentry.text()}>[{messageentry.toPlainText()}]", encoding='utf-8'))

def toggle_idle():
  sock.sendall(bytes(f"§{identity.text()}>toggle_idle>[]", encoding='utf-8'))


def on_exit():
  print('exiting')
  sock.close()

timer = QTimer()
timer.timeout.connect(wait_for_messages)
timer.setInterval(500)

connectbutton.clicked.connect(toggle_connect_to_server)
sendmessagebutton.clicked.connect(send_message)
toggleidlebutton.clicked.connect(toggle_idle)
appInstance.aboutToQuit.connect(on_exit)

timer.start()
window.show()

sys.exit(appInstance.exec_())