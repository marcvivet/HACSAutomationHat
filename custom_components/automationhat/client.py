import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "192.168.0.3"
port = 5683
print(f"Connecting to server {ip} ...")
s.connect((ip, port))

msg = s.recv(1024)
print(msg.decode("utf-8"))