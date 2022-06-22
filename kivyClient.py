import socket

class MySocket:

    def __init__(self,host="localhost",port=45454):
        self.sock = socket.socket()
        self.sock.connect((host, port))
    def get_data(self):
        return self.sock.recv(1024)
    def send_data(self, msg): 
        self.sock.send(msg.encode('ascii'))