"""
Eduardo Júnior Dias dos Santos Moreira 89395
Mateus Armond Santos 89399
"""
import argparse
from connection import server, client


def main():
    parser = argparse.ArgumentParser(description='Main do programa para Cliente/Servidor da troca de mensagens')
    parser.add_argument('type', help='Tipo de execução de programa, C para cliente e S para servidor')
    parser.add_argument('--username', required=False, help='Username do cliente')
    parser.add_argument('--host', required=False, help='Endereco do servidor')
    args = parser.parse_args()

    conn = None
    if args.type == "S" or args.type == "s":
        conn = server.Server()
    elif args.type == "C" or args.type == "c":
        try:
            conn = client.Client(args.username, args.host)
        except Exception as exception:
            print("Argumentos faltando ou servidor offline!")
            return


if __name__ == '__main__':
    main()
