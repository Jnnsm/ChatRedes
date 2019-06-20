import threading
import socket


class Server:
    udp = None
    clients = {}
    def __init__(self, host='', port=2000):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        origem = (host, port)
        self.udp.bind(origem)

        self.listen_udp()
    
    def listen_udp(self):
        while True:
            msg, cliente = self.udp.recvfrom(1024)
            
            print(cliente, msg.decode())
            if(cliente[0] in cliente):
                self.send_msg(msg, cliente[0])
            else:
                msg_decode = msg.decode()
                split_msg = msg_decode.split(':')
                #Adiciona na lista de clientes
                if(split_msg[0] == "USER"):
                    self.clients["split_msg[1]"] = cliente
                    print (self.clients)

            

    def send_msg(self, message, host, port=2000):
        udp_msg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        destino = (host, port)
        udp_msg.sendto(message, destino)