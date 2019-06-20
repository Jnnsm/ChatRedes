import threading
import socket


class Server:
    udp = None
    def __init__(self, host='', port=2000,  ):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        orig = (HOST, PORT)
        udp.bind(orig)
    
    def listen():
        