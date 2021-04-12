# code-server
code-server is backend for the livecode app. This backend code has a client test.py file which you can run and test the server code.

#testing
1. First run the server.py file by typing python3 server.py in the commandline and then run test.py file(if you don't want to use audio then comment 
   the line - import pyaudio by adding # in the beggining of line.
2. To create a meeting send a request to the server from test.py files console 
3. Requests can be of following types
  a) create a meeting format - create:username:meetingname:password
  b) join a meeting format   - join:username:meetingname:password
  c) join audio format       - audio:username:meetingname:password   (this request needs pyaudio to be installed)
4. Now you can start chat with others in the meeting.(but that's on localhost how can you do it online)
5. You can do port forwarding to send your traffic in localhost or wait till i add Firebase support.

