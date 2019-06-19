import threading
import socket


class Client:

    def __init__(self, username, host_address, port=20000):
        self._username = username
        self._host_address = host_address

        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        u.bind((host_address, port))
        thread = threading.Thread(target=self.udp, args=(u,))
        thread.start()

    def udp(self, u):
        while True:
            message, client = u.recvfrom(1024)
            print(client,": ", message.decode())
        u.close()

    def tcp(self):
        pass
