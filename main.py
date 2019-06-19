"""
Eduardo Júnior Dias dos Santos Moreira 89395
Mateus Armond Santos 89399
"""
import argparse
from connection import *


def main():
    parser = argparse.ArgumentParser(description='Main do programa para Cliente/Servidor da troca de mensagens')
    parser.add_argument('type', help='Tipo de execução de programa, C para cliente e S para servidor')
    parser.add_argument('username', required=False, help='Username do cliente')
    args = parser.parse_args()


if __name__ == '__main__':
    main()
