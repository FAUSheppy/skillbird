import socket
from threading import Thread
import NetworkParser

TCP_IP      = '127.0.0.1'
TCP_PORT    = 7041
BUFFER_SIZE = 2048

def listen():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept();
        Thread(target=t_listen,args=(conn,)).start();

def t_listen(conn):
    data = conn.recv(BUFFER_SIZE).decode('utf-8')
    ret = NetworkParser.handleInput(data)
    conn.send(ret)
    conn.close()
