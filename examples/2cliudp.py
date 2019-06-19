import socket
HOST = '127.0.1.1'  # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)
print('Para sair digite bye')
msg = input()
while msg != 'bye':
    udp.sendto (msg.encode(), dest)
    msg = input()
udp.close()
