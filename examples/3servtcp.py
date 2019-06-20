import socket
HOST = ''              # Endereco IP do Servidor
PORT = 20001           # Porta que o Servidor esta
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
			print(msg)
			if msg=='bye':
				break
			print(cliente, msg)
		print('Finalizando conexao do cliente', cliente)
		con.close()
	except Exception as ex:
		print(ex)
