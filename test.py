# this file is only for testing the server. In case of java server add \n to message before sending
# to install pyaudio
# sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
# sudo pip install pyaudio


import socket
# import pyaudio
from time import sleep
from threading import Thread;
import sys
import tkinter
import os	
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
HOST, PORT, BUFFER, FRAMES = "4.tcp.ngrok.io", 14362, 10, 500


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
		self.run = True
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.sock.connect((HOST, PORT))
		except Exception as e:
			print("[CONNECT:SERVER]![connection refused by server]")
		else:
			self.request = self.get_request()
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
							notepad = Notepad(self)
							if self.init_req[0] == "create":
								sender = Thread(target = self.send_text, args = (notepad, )).start()
							if self.init_req[0] == "join":
								recver = Thread(target = self.recv_text, args = (notepad, )).start()
							notepad.run()
		sys.exit(0)

	def get_request(self):
		request = ""
		choice = int(input("CREATE MEETING : 1\nJOIN MEETING : 2\nENTER CHOICE : "))
		if choice == 1:
			request = "create:"
		elif choice == 2:
			request = "join:"
		else:
			print("INCORRECT REQUEST EXITING!")
			sys.exit(0)

		name = str(input("ENTER NAME : "))
		request += name + ":"		
		meeting = str(input("ENTER MEETING ID : "))
		request += meeting + ":"
		password = str(input("ENTER PASSWORD : "))
		request += password
		return request


	@staticmethod
	def get_length(message):
		length = str(len(message));
		length += " "*(BUFFER - len(length))
		return length

	def send_text(self, notepad):
		while self.run:
			message = notepad.get_text()
			# if len(message) == 0:
			# 	continue
			try:
				self.sock.send(self.get_length(message).encode('utf8'))
				self.sock.send((message).encode('utf8'))
			except Exception as e:
				print("[SEND:SERVER]![can't send to server]")
			try:
				sleep(0.1)
			except Exception as e:
				print(e)
				self.run = False

	def recv_text(self, notepad):
		while self.run:
			try:
				length  = int(self.sock.recv(BUFFER).decode('utf8'))
				message = self.sock.recv(length).decode('utf8')
			except Exception as e:
				print("[SEND:SERVER]![can't recv from server]")
			else:
				notepad.set_text(message)

class Notepad:


	def __init__(self, conn):
		self.editor = Tk()

		# default window width and height
		self.__thisTextArea = Text(self.editor)
		self.__thisMenuBar = Menu(self.editor)
		self.__thisFileMenu = Menu(self.__thisMenuBar, tearoff=0)
		self.__thisEditMenu = Menu(self.__thisMenuBar, tearoff=0)
		self.__thisHelpMenu = Menu(self.__thisMenuBar, tearoff=0)

		# To add scrollbar
		self.__thisScrollBar = Scrollbar(self.__thisTextArea)	
		self.__file = None

		# Set icon
		try:
				self.editor.wm_iconbitmap("Notepad.ico")
		except:
				pass

		# Set window size (the default is 300x300)

		self.__thisWidth = 700
		self.__thisHeight = 400

		# Set the window text
		self.editor.title("Online code share")

		# Center the window
		screenWidth = self.editor.winfo_screenwidth()
		screenHeight = self.editor.winfo_screenheight()
	
		# For left-alling
		left = (screenWidth / 2) - (self.__thisWidth / 2)
		
		# For right-allign
		top = (screenHeight / 2) - (self.__thisHeight /2)
		
		# For top and bottom
		self.editor.geometry('%dx%d+%d+%d' % (self.__thisWidth,
											self.__thisHeight,
											left, top))

		# To make the textarea auto resizable
		self.editor.grid_rowconfigure(0, weight=1)
		self.editor.grid_columnconfigure(0, weight=1)

		# Add controls (widget)
		self.__thisTextArea.grid(sticky = N + E + S + W)
		
		# To open new file
		self.__thisFileMenu.add_command(label="New",command=self.__newFile)	
		
		# To open a already existing file
		self.__thisFileMenu.add_command(label="Open",command=self.__openFile)
		
		# To save current file
		self.__thisFileMenu.add_command(label="Save",command=self.__saveFile)	

		# To create a line in the dialog		
		self.__thisFileMenu.add_separator()										
		self.__thisFileMenu.add_command(label="Exit",command=self.__quitApplication)
		self.__thisMenuBar.add_cascade(label="File",menu=self.__thisFileMenu)	
		
		# To give a feature of cut
		self.__thisEditMenu.add_command(label="Cut",command=self.__cut)			
	
		# to give a feature of copy	
		self.__thisEditMenu.add_command(label="Copy",command=self.__copy)		
		
		# To give a feature of paste
		self.__thisEditMenu.add_command(label="Paste",command=self.__paste)		
		
		# To give a feature of editing
		self.__thisMenuBar.add_cascade(label="Edit",menu=self.__thisEditMenu)	
		
		# To create a feature of description of the notepad
		self.__thisHelpMenu.add_command(label="About Notepad",command=self.__showAbout)
		self.__thisMenuBar.add_cascade(label="Help",menu=self.__thisHelpMenu)

		self.editor.config(menu=self.__thisMenuBar)

		self.__thisScrollBar.pack(side=RIGHT,fill=Y)					
		
		# Scrollbar will adjust automatically according to the content		
		self.__thisScrollBar.config(command=self.__thisTextArea.yview)	
		self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)
	
	def get_text(self):
		return self.__thisTextArea.get(1.0, "end-1c")

	def set_text(self, message):
		self.__thisTextArea.delete(1.0, 'end')
		self.__thisTextArea.insert(1.0, message)
		
	def __quitApplication(self):
		conn.run = False
		self.editor.destroy()
		sys.exit(0)

	def __showAbout(self):
		showinfo("Notepad","Hrushikesh Kale ,Rushikesh PBL, Gaurav Bade")

	def __openFile(self):
		
		self.__file = askopenfilename(defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])

		if self.__file == "":
			
			# no file to open
			self.__file = None
		else:
			
			# Try to open the file
			# set the window title
			self.editor.title(os.path.basename(self.__file) + " - Notepad")
			self.__thisTextArea.delete(1.0,END)

			file = open(self.__file,"r")

			self.__thisTextArea.insert(1.0,file.read())

			file.close()

		
	def __newFile(self):
		self.editor.title("Untitled - Notepad")
		self.__file = None
		self.__thisTextArea.delete(1.0,END)

	def __saveFile(self):

		if self.__file == None:
			# Save as new file
			self.__file = asksaveasfilename(initialfile='Untitled.txt',
											defaultextension=".txt",
											filetypes=[("All Files","*.*"),
												("Text Documents","*.txt")])

			if self.__file == "":
				self.__file = None
			else:
				
				# Try to save the file
				file = open(self.__file,"w")
				file.write(self.__thisTextArea.get(1.0,END))
				file.close()
				
				# Change the window title
				self.editor.title(os.path.basename(self.__file) + " - Notepad")
				
			
		else:
			file = open(self.__file,"w")
			file.write(self.__thisTextArea.get(1.0,END))
			file.close()

	def __cut(self):
		self.__thisTextArea.event_generate("<<Cut>>")

	def __copy(self):
		self.__thisTextArea.event_generate("<<Copy>>")

	def __paste(self):
		self.__thisTextArea.event_generate("<<Paste>>")

	def run(self):

		# Run main application
		self.editor.mainloop()

try:
	client = Client()
except Exception as e:
	sys.exit(0)
