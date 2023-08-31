import socket
import sys
import threading
import datetime
import errno
import re
import select
from flask import Flask
from PySide2.QTWidgets import QApplication, QLabel, QWidget, QLineEdit, QGridLayout, QPushButton, QListView
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QIcon, QStandardItem, QStandardItemModel

appInstance = QApplication(sys.argv)

window = QWidget()
windoe.setGeometry(400, 400, 800, 400)
window.setWindowTitle('Planck Server Alpha')

with open("styles.css", "r") as f:
    window.setStyleSheet(f.read())

layout = QGridLayout()

window.setLayout(layout)

window.show()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connections = []
ids = []
statuses = []

online_ct = 0
idle_ct = 0
start_time = 0

server_address = ('localhost', 6626)

def start_server():
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_address)
    sock.settimeout(0.1)
    sock.listen(1)

sys.exit(appInstance.exec_())
