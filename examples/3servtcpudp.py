import threading
import socket
HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

# escutar UDP e TCP na mesma porta
def UDP(udp):
	while True:
		msg, cliente = udp.recvfrom(1024)
		print(cliente, msg.decode())
	udp.close()
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((HOST, PORT))
t = threading.Thread(target=UDP, args=(udp,))
t.start()

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
tcp.bind(orig)
tcp.listen(1)

while True:
	try:
		con, cliente = tcp.accept()
		print('Concetado por', cliente)
		while True:
			msg = con.recv(1024).decode()
			if msg=='bye':
				break
			print(cliente, msg)
		print('Finalizando conexao do cliente', cliente)
		con.close()
	except Exception as ex:
		print(ex)
