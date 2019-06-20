import threading
import socket
import time


class Server:
    udp = None
    clients = {}
    def __init__(self, host='', port=20000):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        origem = (host, port)
        self.udp.bind(origem)

        self.listen_udp()
    
    def listen_udp(self):
        while True:
            msg, cliente = self.udp.recvfrom(1024)
            
            print(cliente, msg.decode())
            if(cliente[0] in self.clients):
                self.resend_msg(msg, cliente[0])
            else:
                
                msg_decode = msg.decode()
                split_msg = msg_decode.split(':')
                
                #Adiciona na lista de clientes
                if(split_msg[0] == "USER"):
                    print("user {} adicionado".format(split_msg[1]) )
                    self.clients[cliente[0]] = (split_msg[1], cliente[1])
                    print (self.clients)

                    self.send_msg("ACK", cliente[0]) #Envia ACK para o cliente conectado

            

    def send_msg(self, message, host, port=20000):
        '''Envia uma mensagem em forma de string'''
        udp_msg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        destino = (host, port)
        udp_msg.sendto(message.encode(), destino)
        udp_msg.close()

    def resend_msg(self, message, host, port=20000):
        '''Envia uma mensagem em bytes mensagem em forma de string'''
        udp_msg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        destino = (host, port)
        udp_msg.sendto(message, destino)
        udp_msg.close()

    def broadcast_exc(self, message, excluded_host, port=20000):
        '''Envia mensagem para todos os usuários menos quem mandou a mensagem e coloca a identificação'''

        #Junta mensagem com a identificação de quem mandou
        new_message = "MSG:{}:".format(self.clients[excluded_host])
        new_message = new_message.encode() + message

        for hosts in self.clients: #Envia a mensagem para os clientes cadastrados
            if hosts != excluded_host:
                self.resend_msg(new_message, hosts, port)

    def broadcast(self, message, excluded_host, port=20000):
        '''Envia mensagem para todos'''

        for hosts in self.clients: #Envia a mensagem para os clientes cadastrados
            if hosts != excluded_host:
                self.resend_msg(message, hosts, port)
            