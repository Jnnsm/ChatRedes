import threading
import socket
import time


class Client:
    """
    Função definida para iniciar as conexões e guardar o username e o endereço e porta do host
    """

    def __init__(self, username, host_address, port=20000):
        self._username = username
        self._host_info = (host_address, port)

        # É criado um socket único para caso a conexão seja fechada para escrita ela também será fechada para ouvir e o
        # programa se encerrará

        u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        u.bind(('', port))

        # Variável que define se o usuário recebeu ou não um ack do servidor
        self.received_ack = False

        # Define a thread para receber mensagens
        thread_receive = threading.Thread(target=self.udp_receive, args=(u,))
        thread_receive.start()

        # Define a primeira mensagem para o servidor é USER: + username
        self.udp_send(u, "USER:" + self._username)

        # Espera resposta do servidor antes de começar um chat, caso ele esteja offline encerra o programa
        start_time = time.time()
        while True:
            if time.time() - start_time > 10 and self.received_ack is False:
                print('Servidor desconectado. Encerrando o programa')
                u.close()
                exit()
            elif self.received_ack is True:
                print('Servidor conectado para chat')
                break

        # Define a thread para entrar no chat
        thread_send = threading.Thread(target=self.chat, args=(u,))
        thread_send.start()

    """
    Função definida para receber mensagens na porta definida em __init__ e responder caso seja necessário
    """

    def udp_receive(self, u):
        while True:
            try:
                message, client = u.recvfrom(1024)
                message = message.decode()
                # Caso a mensagem recebida seja um 'KEEP' responderemos
                if message == 'KEEP':
                    self.udp_send(u, 'KEEP')
                elif message == 'ACK':
                    self.received_ack = True
                # Mostra a mensagem recebida pelo usuário
                else:
                    print(message)
            except Exception as exception:
                break
        u.close()

    """
    Define a função para entrar no chat
    """

    def chat(self, u):
        while True:
            # Recebe uma mensagem de entrada e caso não seja /bye ele envia para o servidor
            message = input()
            if message[0] == '/':
                if message == '/bye':
                    break
                elif message == '/list':
                    self.udp_send(u, 'LIST')
                elif '/get' in message:
                    self.udp_send(u, 'GET' + message[4:])
                elif '/file' in message:
                    self.udp_send(u, 'FILE' + message[5:])
            else:
                message = "MSG:" + message
                self.udp_send(u, message)

        # Envia a mensagem final de que o cliente está saindo
        self.udp_send(u, 'BYE')
        u.close()

    """
    Envia uma mensagem qualquer, por meio de uma conexão U para um target qualquer, o padrão é para o servidor conectado
    """

    def udp_send(self, u, message, target=None):
        # Se não tiver um target especifico mandar para o servidor
        if target is None:
            target = self._host_info
        try:
            u.sendto(message.encode(), target)
        except Exception as excepton:
            return

    def tcp(self):
        pass
