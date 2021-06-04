import socket

HOST = '127.0.0.1'
PORT = 9595
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST,PORT))

try:

    while True:
        msg = input()
        
        socket.sendall(msg.encode())
        data  = socket.recv(1024)
        if not data:
            print('Connection lost')
            break
        
        while not '[END]' in data.decode():
            print(data.decode())
            data = socket.recv(1024)
        
        print(data.decode())
except:
     print('GG')
     socket.close()