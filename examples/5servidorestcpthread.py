import socket
import threading

HOST = ''              # Endereco IP do Servidor
PORT = 5000            # Porta que o Servidor esta

def conectado(con, cliente):
    print('Conectado por', cliente)

    while True:
        msg = con.recv(1024).decode()
        if msg=='bye':
            break
        print(cliente, msg)

    print('Finalizando conexao do cliente', cliente)
    con.close()
    return

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

orig = (HOST, PORT)

tcp.bind(orig)
tcp.listen(1)

while True:
    con, cliente = tcp.accept()
    t = threading.Thread(target=conectado, args=(con, cliente))
    t.start()

tcp.close()
