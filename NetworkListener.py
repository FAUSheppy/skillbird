import socket
from threading import Thread
import NetworkParser

TCP_IP      = '127.0.0.1'
TCP_PORT    = 7040
# must be same as smmod
BUFFER_SIZE = 1024

def listen():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(5)
    print("TCP listener on {}:{}".format(TCP_IP, TCP_PORT))
    while True:
        conn, addr = s.accept();
        Thread(target=t_listen,args=(conn,)).start();

def t_listen(conn):
    while True:
        try:
            data = conn.recv(BUFFER_SIZE).decode('utf-8')
            # data is only None if the connection is seperated
            if not data:
                break
            ret = NetworkParser.handleInput(data)
            if not ret:
                ret = "Rating Backend Error"
            if type(ret) == str:
                ret = ret.encode("utf-8")
            conn.send(ret)
        except IOError:
            pass
