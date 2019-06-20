import threading
import socket
import time


class Server:
    udp = None
    tcp = None
    port = None
    clients = {}
    keep_time = 0
    def __init__(self, host='', port=20000):
        self.port = port
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        origem = (host, port)
        self.udp.bind(origem)

        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.bind(tcp.bind(orig))

        self.keep_time = time.time()

        self.listen_udp()
    
    def listen_udp(self):
        while True:
            msg, cliente = self.udp.recvfrom(1024)
            
            msg_decode = msg.decode()
            print(cliente, msg.decode())

            if(msg_decode == 'BYE'): #retira cliente da lista de conectados
                    print("Cliente {} desconectou".format(self.clients[cliente[0]][0]))
                    del self.clients[cliente[0]]
            elif(msg_decode == 'LINK'):
                for k in self.clients:
                    self.send_msg(self.clients[k][0], cliente[0])
            elif( 'FILE' == msg_decode[0:4] ):
                pass
            elif(cliente[0] in self.clients):
                self.broadcast_exc(msg_decode, cliente[0], self.port)
            else:
                split_msg = msg_decode.split(':')
                
                #Adiciona na lista de clientes
                if(split_msg[0] == "USER"):
                    print("user {} adicionado".format(split_msg[1]) )
                    self.clients[cliente[0]] = (split_msg[1], cliente[1])
                    print (self.clients)

                    self.send_msg("ACK", cliente[0]) #Envia ACK para o cliente conectado

            #Envia KEEP a cada 10 segundos
            if time.time() - self.keep_time > 10:
                self.broadcast("KEEP")
        self.udp.close()
    

    def send_msg(self, message, host, port=20000):
        '''Envia uma mensagem em forma de string'''
        destino = (host, port)
        self.udp.sendto(message.encode(), destino)

    def resend_msg(self, message, host, port=20000):
        '''Envia uma mensagem em bytes mensagem em forma de string'''
        destino = (host, port)
        self.udp.sendto(message, destino)

    def broadcast_exc(self, message, excluded_host, port=20000):
        '''Envia mensagem para todos os usuários menos quem mandou a mensagem e coloca a identificação'''

        #Junta mensagem com a identificação de quem mandou
        new_message = "MSG:{}:{}".format(self.clients[excluded_host], message)

        for hosts in self.clients: #Envia a mensagem para os clientes cadastrados
            if hosts != excluded_host:
                self.send_msg(new_message, hosts, port)

    def broadcast(self, message, port=20000):
        '''Envia mensagem para todos os clientes cadastrados'''

        for hosts in self.clients:
            self.send_msg(message, hosts, port)
            