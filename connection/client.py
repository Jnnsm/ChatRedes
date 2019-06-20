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

        self._u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._u.bind(('', port))

        self._t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._t.bind(('', port))

        # Variável que define se o usuário recebeu ou não um ack do servidor
        self.received_ack = False

        # Define a thread para receber mensagens
        thread_receive = threading.Thread(target=self.udp_receive)
        thread_receive.start()

        # Define a primeira mensagem para o servidor é USER: + username
        self.udp_send("USER:" + self._username)

        # Espera resposta do servidor antes de começar um chat, caso ele esteja offline encerra o programa
        start_time = time.time()
        while True:
            if time.time() - start_time > 10 and self.received_ack is False:
                print('Servidor desconectado. Encerrando o programa')
                self._u.close()
                exit()
            elif self.received_ack is True:
                print('Servidor conectado para chat')
                break

        # Define a thread para entrar no chat
        thread_send = threading.Thread(target=self.chat)
        thread_send.start()

    """
    Função definida para receber mensagens na porta definida em __init__ e responder caso seja necessário
    """

    def udp_receive(self):
        while True:
            try:
                message, client = self._u.recvfrom(1024)
                message = message.decode()
                # Caso a mensagem recebida seja um 'KEEP' responderemos
                if message == 'KEEP':
                    self.udp_send('KEEP')
                # Caso recebemos um ack, confirmamos por meio da variável booleana global received_ack
                elif message == 'ACK':
                    self.received_ack = True
                # Caso recebemos um info mostramos o conteúdo da informação na tela
                elif "INFO:" in message:
                    print(message[6:])
                # Mostra a mensagem recebida pelo usuário
                else:
                    print(message)
            except Exception as exception:
                break
        self._u.close()

    """
    Define a função para entrar no chat
    """

    def chat(self):
        while True:
            # Recebe uma mensagem de entrada e caso não seja /bye ele envia para o servidor
            message = input()
            if message[0] == '/':
                # Caso seja uma mensagem de finalização saimos do loop
                if message == '/bye':
                    break
                # Caso seja um pedido de lista envia a palavra chave LIST
                elif message == '/list':
                    self.udp_send('LIST')
                # Caso seja um get de um arquivo envia a palavra chave GET com o nome do arquivo logo em seguida, além
                # de estabelecer uma conexão tcp para essa transferencia
                elif '/get' in message:
                    self.udp_send('GET' + message[4:])
                    thread_tcp_receive = threading.Thread(target=self.tcp_receive, args=(message[5:],))
                    thread_tcp_receive.start()
                # Caso seja a inserção de um arquivo envia a palavra FILE e o nome do arquivo, além de estabelecer uma
                # conexão tcp para essa transferencia
                elif '/file' in message:
                    self.udp_send('FILE' + message[5:])
                    thread_tcp_send = threading.Thread(target=self.tcp_send, args=(message[6:],))
                    thread_tcp_send.start()
            else:
                message = "MSG:" + message
                self.udp_send(message)

        # Envia a mensagem final de que o cliente está saindo
        self.udp_send('BYE')
        self._u.close()

    """
    Envia uma mensagem qualquer, por meio de uma conexão U para um target qualquer, o padrão é para o servidor conectado
    """

    def udp_send(self, message, target=None):

        # Se não tiver um target especifico mandar para o servidor
        if target is None:
            target = self._host_info
        try:
            self._u.sendto(message.encode(), target)
        except Exception as exception:
            print(exception)

    def tcp_receive(self, filename):
        print("Recebendo arquivo " + filename)
        # Faz as redefinições do TCP
        self._t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._t.bind(('', self._host_info[1]))
        self._t.listen(1)
        try:
            # Abre arquivo para escrita binária
            file = open(filename, "wb")
            # Aceita a conexão com o sender
            connection, sender = self._t.accept()
            while True:
                # Recebe uma mensagem e logo em seguida escreve ela no arquivo caso não seja um BYE
                message = connection.recv(1024)
                if 'BYE'.encode() in message:
                    break
                file.write(message)
            # Fecha as conexões e o arquivo
            connection.close()
            self._t.close()
            file.close()
        except Exception as exception:
            print(exception)
        print("Arquivo recebido")

    def tcp_send(self, filename):
        print("Enviando arquivo " + filename)
        # Redefine o socket de tcp
        self._t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Testa conexão com o host
            self._t.connect(self._host_info)
            # Abre arquivo escolhido
            file = open(filename, "rb")
            # Lê 32 bytes de um arquivo
            data = file.read(32)
            # Enquanto o dado pego do arquivo não for vazio envia o dado e pega mais 32 bytes
            while data != b'':
                self._t.send(data)
                data = file.read(32)
            # Envio terminado, envia um BYE para simbolizar
            self._t.send('BYE'.encode())
            # Fecha o arquivo e a conexão
            file.close()
            self._t.close()
        except Exception as exception:
            print(exception)

        print("Arquivo enviado")
