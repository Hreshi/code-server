# this file is only for testing the server. In case of java server add \n to message before sending
# to install pyaudio
# sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
# sudo pip install pyaudio


import socket
import pyaudio
from time import sleep
from threading import Thread;

HOST, PORT, BUFFER, FRAMES = "0.tcp.ngrok.io", 12765, 10, 500


# voice chat is second thread in client
# when user clicks on join audio button create this object and call .start() method
class Voice_chat(Thread):

	def __init__(self,req_list, sock):
		Thread.__init__(self)
		self.sock        = sock
		self.meeting_key = req_list[2]
		self.meeting_val = req_list[3]
		self.username    = req_list[1]
		self.init_req    = "audio:" + self.username + ":" + self.meeting_key + ":" + self.meeting_val
		self.audio_player = pyaudio.PyAudio()
		self.playing_stream = self.audio_player.open(format=pyaudio.paInt16, channels=1, rate=20000, output=True, frames_per_buffer=FRAMES)
		self.recording_stream = self.audio_player.open(format=pyaudio.paInt16, channels=1, rate=20000, input=True, frames_per_buffer=FRAMES)
		self.kill_thread = False

	def receive_audio(self):
		while not self.kill_thread:
			try:
				data = self.sock.recv(FRAMES)
				self.playing_stream.write(data)
			except Exception as e:
				print("cannot play audio : ", e)


	def send_audio(self):
		while not self.kill_thread:
			try:
				data = self.recording_stream.read(FRAMES)
				self.sock.send(data)
			except Exception as e:
				print("cannot record audio : ", e)


	def run(self):
		# try:
		# 	self.sock.connect((HOST, PORT))
		# except Exception as e:
		# 	return
		
		# print("[AUDIO:SUCCESS]![connected to server]")

		# try:
		# 	self.sock.send(Client.get_length(self.init_req).encode('utf8'))
		# 	self.sock.send((self.init_req).encode('utf8'))
		# except Exception as e:
		# 	print(e)
		# 	return
		
		# print("[AUDIO:SUCCESS]![request send to server]")

		# try:
		# 	length  = int(self.sock.recv(BUFFER).decode('utf8'))
		# 	message = self.sock.recv(length).decode('utf8') 
		# except Exception as e:
		# 	return

		# print(message)
		# if "1" in message:
		thread = Thread(target = self.send_audio).start()
		self.receive_audio()


# Client is main thread
# when user clicks join/create meeting create this object
# for now "audio" is handled by this class audio not working
class Client:

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.sock.connect((HOST, PORT))
		except Exception as e:
			print("[CONNECT:SERVER]![connection refused by server]")
		else:
			self.request = input()
			self.init_req = self.request.split(":")
			try:
				self.sock.send((self.get_length(self.request)).encode('utf8'))
				self.sock.send((self.request).encode('utf8'))
			except Exception as e:
				print("[SEND:SERVER]![connection pipeline broken] : " , e)
			else:
				try:
					length = int(self.sock.recv(BUFFER).decode('utf8'))
					self.response = self.sock.recv(length).decode('utf8')
					print(self.response)
				except Exception as e:
					print("[RECEIVE:SERVER]![connection pipeline broken]")
				else:
					if "1" in self.response:
						if self.init_req[0] == "audio":
							voice_chat = Voice_chat(self.init_req, self.sock)
							voice_chat.start()
						else:
							thread = Thread(target = self.send_text, args = ()).start()
							self.recv_text()

	@staticmethod
	def get_length(message):
		length = str(len(message));
		length += " "*(BUFFER - len(length))
		return length

	def send_text(self):
		while 1:
			message = input("Enter message : ")
			if message == "exit":
				self.sock.close()
				break
			try:
				self.sock.send(self.get_length(message).encode('utf8'))
				self.sock.send((message).encode('utf8'))
			except Exception as e:
				print("[SEND:SERVER]![can't send to server]")

	def recv_text(self):
		while 1:
			try:
				length  = int(self.sock.recv(BUFFER).decode('utf8'))
				message = self.sock.recv(length).decode('utf8')
			except Exception as e:
				print("[SEND:SERVER]![can't recv from server]")
			else:
				print(message)

client = Client()