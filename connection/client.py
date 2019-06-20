import threading
import socket


class Client:

    def __init__(self, username, host_address, port=20000):
        self._username = username
        self._host_info = (host_address, port)

        u_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        u_receive.bind(self._host_info)

        thread_receive = threading.Thread(target=self.udp_receive, args=(u_receive,))
        thread_receive.start()

        u_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        thread_send = threading.Thread(target=self.udp_send, args=(u_send,))
        thread_send.start()

    def udp_receive(self, u):
        while True:
            message, client = u.recvfrom(1024)
            print(message.decode())
        u.close()

    def udp_send(self, u, target=None):
        if target is None:
            target = self._host_info
        message = "USER:" + self._username
        while message != '/bye':
            u.sendto(message.encode(), target)
            message = "MSG:" + input()
        u.close()

    def tcp(self):
        pass
