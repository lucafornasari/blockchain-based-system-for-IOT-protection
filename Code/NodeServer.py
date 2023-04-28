import threading
import socket

class NodeServer(threading.Thread):

    def __init__(self, port, dat):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', port))
        self.socket.listen(5)
        self.data = dat
        print(f"Server started on port {port}")

    def run(self):
        while True:
            client, address = self.socket.accept()
            print(f"Connection from {address} established")
            client.send(bytes(self.data, "utf-8"))