# this file is only for testing the server. In case of java server add \n to message before sending

import socket;
from threading import Thread;

HOST = "127.0.0.1"
PORT = 5000
BUFFER = 10
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def to_int(message):
	length = str(len(message));
	length += " "*(BUFFER - len(length))
	return length

def sender():
	global client
	while True:
		message = input()
		client.send(to_int(message).encode('utf8'))
		client.send(message.encode('utf8'))
		if message == "EXIT":
			break

def receiver():
	global client
	print("Thread is running")
	while True:
		len = client.recv(BUFFER).decode('utf8')
		message = client.recv(int(len))
		print(message.decode('utf8'))
		if message == "EXIT":
			break



def main():
	global client
	client.connect((HOST, PORT))
	thread = Thread(target=receiver, args = ())
	thread.start()
	sender()
	client.close()


main()