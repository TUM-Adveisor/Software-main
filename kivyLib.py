import socket
import subprocess
from threading import Thread
import time
import select


###################################################################
#                    kivyLib Documentation 
# Features: Socket communication with GUI, autostart GUI
# 
# Usage: 
#      send_data([message, comma seperated])
#           Usable command now: 
#               "hehe" -> start new round for GUI
#               "move, [chess move notation]" -> makes move from GUI 
#      get_data(), returns string with recieved data
#      processData(), returns array with commands
#
###################################################################
serversocket = socket.socket()

host = 'localhost'
port = 45454

data = ""
serversocket.bind(('', port))

subprocess.Popen(["kivy_venv\Scripts\python.exe", "gui.py"])
serversocket.listen(1)

clientsocket,addr = serversocket.accept()
clientsocket.setblocking(0)
print("got a connection from %s" % str(addr))	

def send_data(msg):
    clientsocket.send(msg.encode('ascii'))
    time.sleep(0.01)
def get_data():
    ready = select.select([clientsocket], [], [], 0.5)
    if ready[0]:
        return clientsocket.recv(1024).decode("ascii")
    else:
        return "False"
def processData():
    cmd = get_data().split(",")
    return cmd
#while True:
#    msg = input(">")
#    clientsocket.send(msg.encode('ascii'))
