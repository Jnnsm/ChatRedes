import threading
import socket
import time
import select

import sys
sys.path.insert(0,'/arquivos')


class Server:
    '''
    Classe que cria e gerencia as conexões e todas as operações em modo servidor
    '''

    udp = None
    tcp = None
    port = None
    clients = {}
    def __init__(self, host='', port=20000):
        self.port = port

        #Cria a conexão UDP
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        origem_udp = (host, port)
        self.udp.bind(origem_udp)

        #Cria a conexão TCP
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        origem_tcp = (host, port)
        self.tcp.bind(origem_tcp)
        self.tcp.listen(1)

        #Thread criada para mandar a mensagem KEEP a cada 10 segundos
        self.stop_keep = False
        keep_thread = threading.Thread(target=self.keep_sender)
        keep_thread.start()


        #Cria uma thread para verificar entradas de teclado
        input_thread = threading.Thread(target=self.check_input)
        input_thread.start()


        #Chama a função principal responsável pelo funcionamento do servidor
        self.listen_udp()

    def check_input(self):
        _input = input()
        if(_input == "/shutdown"):
            self.close()

    def close(self):
        try:
            self.udp.close()
            self.tcp.close()
            exit()
            return
        except Exception as e:
            print(e)
            exit()
            return

        return
    
    def listen_udp(self):
        '''
        Função definida para gerenciar todas as mensagem recebidas
        '''

        while True:

            msg, cliente = self.udp.recvfrom(1024)
            
            msg_decode = msg.decode()
            print(cliente, msg.decode())

            if(msg_decode == 'BYE'): #Retira cliente da lista de conectados se receber BYE
                    print("Cliente {} desconectou".format(self.clients[cliente[0]][0]))
                    self.broadcast("INFO: Usuário {} se desconectou".format(self.clients[cliente[0]][0]), cliente[0], port = self.port)
                    del self.clients[cliente[0]]

            elif(msg_decode == 'LINK'): #Envia a lista de clientes conectados se receber LINK
                for k in self.clients:
                    self.send_msg(self.clients[k][0], cliente[0], self.port)

            elif(msg_decode == 'KEEP'): #Zera a penalidade do KEEP se o cliente responder
                self.clients[cliente[0]][2] = 0
            
            elif(msg_decode == 'LIST'): #Envia a lista de clientes para quem solicitou
                self.send_msg("Clientes conectados:", cliente[0], self.port)
                for k in self.clients:
                    self.send_msg(self.clients[k][0], cliente[0], self.port)

            elif( 'FILE' == msg_decode[0:4] ): #Recebe um arquivo
                self.create_tcp_thread_receive(msg_decode[5:])

            elif( 'GET' == msg_decode[0:3] ): #Envia um arquivo
                self.create_tcp_thread_send(msg_decode[3:], cliente[0], self.port)

            elif('MSG' == msg_decode[0:3] and cliente[0] in self.clients): #Faz um broadcast da mensagem enviada
                message_to_resend = "MSG:{}:{}".format(self.clients[cliente[0]][0],msg_decode[4:])
                self.broadcast(message_to_resend, cliente[0], port = self.port)

            elif('USER' == msg_decode[0:4]): #Adiciona cliente na lista de clientes conectados
                split_msg = msg_decode.split(':')
                
                if(split_msg[0] == "USER"):
                    print("User {} adicionado a lista de usuário".format(split_msg[1]) )
                    self.clients[cliente[0]] = [split_msg[1], cliente[1], 0]

                    self.send_msg("ACK", cliente[0], self.port) #Envia ACK para o cliente conectado

                    #Gera uma INFO informando a entrada do novo usuário
                    self.broadcast("INFO: Usuário {} se conectou".format(split_msg[1]), cliente[0], port = self.port)

        

    def create_tcp_conn_receive(self, conn, cliente_tcp, file_name = ''):
        '''
        Função definida para aceitar a conexão receber, criar uma thread para a mesma
        e receber o arquivo
        '''

        print('Iniciando conexao TCP com o cliente', self.clients[cliente_tcp[0]])
        with open(file_name,"wb") as f:
            while True:
                arq = conn.recv(2048)
                if('BYE'.encode() in arq):
                    break

                f.write(arq)

        print('Finalizando conexao TCP do cliente', self.clients[cliente_tcp[0]])
        conn.close()
        message_to_resend = "INFO: Usuário {} disponibilizou o arquivo {} no servidor\
                                ".format(self.clients[cliente_tcp[0]][0],file_name)
        self.broadcast(message_to_resend, cliente_tcp[0], port = self.port)
        return

    def create_tcp_thread_receive(self, file_name = ''):
        '''
        Função definida para aceitar a conexão e criar uma thread para a mesma
        '''

        conn, cliente_tcp = self.tcp.accept()
        tcp_thread_receive = threading.Thread(target=self.create_tcp_conn_receive, args=(conn, cliente_tcp, file_name))
        tcp_thread_receive.start()

    def create_tcp_conn_send(self, host, port=20000, file_name = ''):
        '''
        Função definida para aceitar a conexão receber, criar uma thread para a mesma
        e enviar o arquivo
        '''

        tcp_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        with open(file_name, "rb") as f:
            # Lê 32 bytes de um arquivo
            data = f.read(32)

            #Conecta com o cliente
            tcp_send.connect( (host, port) )

            # Enquanto o dado pego do arquivo não for vazio envia o dado e pega mais 32 bytes
            while data != b'':
                tcp_send.send(data)
                data = f.read(32)

        # Envio terminado, envia um BYE para simbolizar
        tcp_send.send('BYE'.encode())

        # Fecha a conexão
        tcp_send.close()

        return

    def create_tcp_thread_send(self, file_name, host, port=20000):
        '''
        Função definida para aceitar a conexão e criar uma thread para a mesma
        '''
        tcp_thread_send = threading.Thread(target=self.create_tcp_conn_send, args=(host, port, file_name))
        tcp_thread_send.start()

    
    def keep_sender(self):
        '''
        Função definida para enviar KEEP a cada 10 segundos
        (Ser usada em uma thread) 
        '''

        try:
            keep_time = time.time()
            while True:
                if select.select([], [self.udp], [], 1)[1]:
                    if time.time() - keep_time > 10:
                        #Penaliza em um o cliente que não mandar o KEEP e checa os que não respoderam dois KEEP
                        abscent_client = []
                        for k in self.clients:
                            if self.clients[k][2] == -3:
                                print("Cliente {} desconectou por não reenviar o KEEP".format(self.clients[k][0]))
                                abscent_client.append(k)
                            else:
                                self.clients[k][2] -= 1

                        #Excluí os clientes ausentes por mais de dois KEEP e informa os usuários
                        for k in abscent_client:
                            self.broadcast("INFO: Usuário {} se desconectou por\
                                            inatividade".format(self.clients[k][0]),
                                            self.clients[k][0], port = self.port)
                            del self.clients[k]

                        #Envia a messagem KEEP para todos os usuários
                        self.broadcast("KEEP", port = self.port)

                        #Tempo é zerado
                        keep_time = time.time()
        except Exception as e:
            return


    def send_msg(self, message, host, port=20000):
        '''
        Função atômica para enviar uma mensagem com o host, string e porta passadas como parâmetro
        '''
        destino = (host, port)
        self.udp.sendto(message.encode(), destino)

    def broadcast(self, message, excluded_host = [], port=20000):
        '''
        Função definida para enviar mensagens para todos os usuários
        exceto os da lista passados como parâmetro
        '''

        for hosts in self.clients: #Envia a mensagem para os clientes cadastrados
            if hosts not in excluded_host:
                self.send_msg(message, hosts, port)