import socket
import os
import sys
from threading import Thread, Condition
from time import sleep
from queue import Queue

# global variables
PORT, BUFFER = 5000, 10

class Request_queue(Thread):

	request_queue = Queue(0)

	def __init__(self):
		Thread.__init__(self)

	def create_meeting(self, client):
		if client.init_req[2] in Server.meeting_list:
			client.response = "0:Meeting already exists!"
		else:
			meeting = Meeting(client)
			meeting.participant.append(client)
			Server.meeting_list[client.init_req[2]] = meeting
			client.response = "1:success"

	def run(self):
		while True:
			while not self.request_queue.empty():
				client = self.request_queue.get()
				self.create_meeting(client)
				client.can_run = True

			if self.request_queue.empty():
				sleep(1)

# ***** client *****

class Meeting:

	def __init__(self, client):
		self.meeting_key = client.init_req[2]
		self.meeting_val = client.init_req[3]
		self.host_sock   = client.sock
		self.host_name   = client.username
		self.participant = []
		self.audio_group = []

	def join(self, client):
		self.participant.append(client)

	def leave(self, client):
		self.participant.remove(client)

# ***** client ***** 

class Client(Thread):

	def __init__(self, sock):
		Thread.__init__(self)
		self.sock = sock
		self.username = ""
		self.init_req = []
		self.message = ""
		self.response = "Invalid request! Try again"
		self.can_run = False
		self.kill_thread = False

	def valid_request(self):
		# returns tru if request is valid
		return len(self.init_req) == 4 and self.init_req[0] in ["join", "create", "audio"]

	def get_length(self, message):
		length = str(len(message));
		length += " "*(BUFFER - len(length))
		return length

	def join_request(self):
		if self.init_req[2] in Server.meeting_list:
			meeting = Server.meeting_list[self.init_req[2]]
			if self.init_req[3] == meeting.meeting_val:
				meeting.join(self)
				return "1:success"
			else:
				return "0:Incorrect credentials!"
		else:
			return "0:Meeting does not exist!"

		return "2:ERROR"

	def create_request(self):
		Request_queue.request_queue.put(self)

	def join_audio(self):
		if self.init_req[2] in Server.meeting_list:
			meeting = Server.meeting_list[self.init_req[2]]
			if self.init_req[3] == meeting.meeting_val:
				meeting.audio_group.append(self)
				return "1:success"
			else:
				return "0:Incorrect credentials!"
		else:
			return "0:Meeting does not exist!"

		return "2:ERROR"

	def voice_broadcast(self, data, meeting):

		for user in meeting.audio_group:
			conn = user.sock
			if conn == self.sock:
				continue

			try:
				conn.send(data)
			except Exception as e:
				pass

	# thread starts here
	def run(self):
		length = int(self.sock.recv(BUFFER).decode('utf8'))
		self.message = self.sock.recv(length).decode('utf8')
		self.init_req = self.message.split(':')

		if self.valid_request():
			self.username = self.init_req[1]

			if self.init_req[0] == "join":
				self.response = self.join_request()
			elif self.init_req[0] == "create":
				self.create_request()
			elif self.init_req[0] == "audio":
				self.response = self.join_audio()

			# wait for Request_queue to finish processing request
			if self.init_req[0] == "create":
				while not self.can_run:
					sleep(1)
					
			self.sock.send(self.get_length(self.response).encode('utf8'))
			self.sock.send(self.response.encode('utf8'))


			if "1" in self.response and self.init_req[0] != "audio":
				while not self.kill_thread:
					try:
						length = int(self.sock.recv(BUFFER).decode('utf8'))
						message = self.sock.recv(length).decode('utf8')
					except:
						print("can't read from host")
						message = "host_gone"
						self.kill_thread = True
					meeting = Server.meeting_list[self.init_req[2]]
					for user in meeting.participant:
						conn = user.sock
						if conn == self.sock:
							continue
						try:
							conn.send(self.get_length(message).encode('utf8'))
							conn.send(message.encode('utf8'))
						except Exception as e:
							meeting.participant.remove(user)

			elif self.init_req[0] == "audio":
				meeting = Server.meeting_list[self.init_req[2]]
				while not self.kill_thread:
					try:
						data = self.sock.recv(1024)
						self.voice_broadcast(data, meeting)
					except Exception as e:
						pass
					
		else:
			self.sock.send(self.get_length("Incorrect request!").encode('utf8'))
			self.sock.send("Incorrect request!".encode('utf8'))

		self.sock.close()



# ***** server code here *****

class Server:
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	meeting_list, host = {}, ""

	def __init__(self, port):
		self.port = port

	# setup of server, working fine
	def prepare(self):
		try:
			self.server.bind((self.host, self.port))
		except Exception as e:
			os.system("kill -9 $(lsof -t -i:{})".format(self.port))
			os.system("kill -9 $(lsof -t -i:{})".format(self.port))
			try:
				self.server.bind((self.host, self.port))
			except Exception as e:
				print(e)
				sys.exit(0)
			else:
				self.server.listen(5)
		else:
			self.server.listen(5)

	# client accepting loop
	def start(self):
		self.prepare()
		run = True
		while run:
			
			try:
				sock, addr = self.server.accept()
				print("user connected!")
			except Exception as e:
				print("server stopped accepting users!")
				run = False
			else:
				client = Client(sock)
				client.start()
		self.server.close()

# main code execution here

def main():
	request_handler = Request_queue()
	livecode = Server(PORT)
	request_handler.start()
	livecode.start()

main()