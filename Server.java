import java.net.ServerSocket;
import java.net.Socket;
import java.io.PrintWriter;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Queue;
import java.util.ArrayList;
import java.util.LinkedList;


// this is server written in java

public class Server {
	static ArrayList<Meeting>meetingList;
	static Queue<Client>requestQueue;
	static ServerSocket server;

	Server(int port){
		try
		{
			server       = new ServerSocket(port);
			meetingList  = new ArrayList<Meeting>();
			requestQueue = new LinkedList<Client>();
			new Meeting(meetingList);
			new HandleClient(requestQueue);
		}
		catch(Exception e)
		{
			System.out.println("Server() : " + e);
			System.exit(0);
		}
	}
	public static void main(String args[]){
		Server server = new Server(Integer.parseInt(args[0]));
		RequestQueueHandler reqHandler = new RequestQueueHandler(meetingList, requestQueue);
		reqHandler.start();
		server.start();

	}

	private void start(){
		Socket sock;
		while(true){
			try
			{
				sock = server.accept();
			}
			catch(Exception e)
			{
				System.out.println("start() : " + e);
				continue;
			}
			System.out.println("CLIENT CONNECTED");
			HandleClient handle = new HandleClient(sock);
			handle.start();

		}
	}
}

class HandleClient extends Thread{
	static Queue<Client>requestQueue;
	PrintWriter writer;
	BufferedReader reader;
	Socket sock;
	String request[];
	Client client;

	HandleClient(Queue<Client>queue){
		requestQueue = queue;
	}

	HandleClient(Socket sock){
		this.sock = sock;
		try
		{
			reader = new BufferedReader(new InputStreamReader(sock.getInputStream()));
			writer = new PrintWriter(sock.getOutputStream(), true);
		}
		catch(Exception e)
		{
			System.out.println("HandleClient() : " + e);
		}
	}
	public void run(){
		try
		{
			String req  = reader.readLine();
			System.out.println(req);
			request = req.split(":");
		}
		catch(Exception e)
		{
			return;
		}
		if(!validRequest(request)){
			return;
		}
		client = new Client(sock, request);
		if(request[0].equalsIgnoreCase("join")){
			int code = Meeting.joinRequest(client);
			if(code < 4 && code > -1){
				try
				{
					writer.println(messageLen(Message.join[code]));
					writer.println(Message.join[code]);
				}
				catch(Exception e)
				{
					System.out.println("run().join : " + e);
					return;
				}
			}
		}
		else if(request[0].equalsIgnoreCase("create")){
			requestQueue.add(client);
			System.out.println("ADDED TO Q");
			return;
		}
		// while(true){
		// 	try
		// 	{
		// 		String message = reader.readLine();
		// 		System.out.println(message);
		// 	}
		// 	catch(Exception e)
		// 	{
		// 		System.out.println("after cmd  : " + e);
		// 		break;
		// 	}
		// }
	}

	public boolean validRequest(String req[]){
		if(req.length == 4 && (req[0].equals("create") || req[0].equals("join") || req[0].equals("del"))){
			return true;
		}
		return false;
	}
	public static String messageLen(String message){
		String blank = "                 do not touch";
		String len   = (message.length()+1) + "";
		len         += blank.substring(0, 9 - len.length());
		return len;  
	}
}

class RequestQueueHandler extends Thread{
	static ArrayList<Meeting>meetingList;
	static Queue<Client>requestQueue;
	PrintWriter writer;

	RequestQueueHandler(ArrayList<Meeting>list, Queue<Client>queue){
		meetingList  = list;
		requestQueue = queue;
	}

	public void run(){
		while(true){
			while(!requestQueue.isEmpty()){
				Client client = requestQueue.peek();
				boolean meetingExists = false;
				if(client.request[0].equalsIgnoreCase("create")){
					for(Meeting meeting : meetingList){
						if(meeting.meetingID.equalsIgnoreCase(client.request[2])){
							meetingExists = true;
						}
					}
					handle(client, meetingExists);
					System.out.println("REQUEST HANDLED");
					requestQueue.remove();
				}
			}
			if(requestQueue.isEmpty()){
				try
				{
					Thread.sleep(1000);
				}
				catch(Exception e)
				{
					System.out.println("thread cant sleep" + e);
				}
			}
			for(Meeting meeting : meetingList){
				System.out.println("Meeting host : " + meeting.host.request[1]);
				System.out.println("Number of clients : " + meeting.participants.size());
			}
		}
	}

	private void handle(Client client, boolean meetingExists){
		try
		{
			writer = new PrintWriter(client.sock.getOutputStream(), true);
		}
		catch(Exception e)
		{

		}
		if(meetingExists){
			try
			{
				writer.println(HandleClient.messageLen(Message.create[0]));
				writer.println(Message.create[0]);
				client.sock.close();
			}
			catch(Exception e)
			{
				System.out.println("handle().exists " + e);
			}
			System.out.println("MEETING EXISTS");
		}else{
			Meeting meeting = new Meeting(client);
			meetingList.add(meeting);
			DataStreamer host = new DataStreamer(meeting.participants);
			host.start();
			System.out.println("ADDED TO MEETINGS");
			writer.println(HandleClient.messageLen(Message.create[1]));
			writer.println(Message.create[1]);
		}
	}
}

class DataStreamer extends Thread{
	PrintWriter writer;
	BufferedReader reader;
	Socket sock;
	ArrayList<Client>participants;
	String message;

	DataStreamer(ArrayList<Client>list){
		participants = list;
		sock = list.get(0).sock;
		try
		{
			reader = new BufferedReader(new InputStreamReader(sock.getInputStream()));
		}
		catch(Exception e)
		{
			System.out.println(e);
			return;
		}
	}

	public void run(){
		while(true){
			try
			{
				message = reader.readLine();
			}
			catch(Exception e)
			{
				System.out.println(e);
			}
			for(int i = 1;i < participants.size();i++){
				Client client = participants.get(i);
				try
				{
					writer = new PrintWriter(client.sock.getOutputStream());
					writer.println(HandleClient.messageLen(message));
					writer.println(message);
				}
				catch(Exception e)
				{
					participants.remove(client);
					System.out.println("CLIENT REMOVED");
				}
			}
		}
	}
}
class Meeting {
	static ArrayList<Meeting>meetingList;
	Client host;
	String meetingID, meetingKey;
	ArrayList<Client>participants;

	Meeting(ArrayList<Meeting>list){
		meetingList  = list;
	}
	Meeting(Client host){
		this.meetingID  = host.request[2];
		this.meetingKey = host.request[3];
		this.host       = host;
		participants    = new ArrayList<Client>();
		participants.add(host);
	}

	public static int joinRequest(Client client){
		for(Meeting meeting : meetingList){
			if(meeting.meetingID.equalsIgnoreCase(client.request[2])){
				if(meeting.meetingKey.equalsIgnoreCase(client.request[3])){
					meeting.participants.add(client);
					return 1;
				}else{
					return 2;
				}
			}
		}
		return 0;
	}
}

class Client {
	Socket sock;
	String request[];

	Client(Socket sock, String req[]){
		this.sock = sock;
		request = req;
	}
}

//error or signal messages
class Message{
	static String join[] = {
								"No such meeting exists!", 
								"Success",
								"Invalid credentials"
						};
	static String create[] = {
								"Meeting already exists!",
								"Success",
								"Invalid credentials"
						};
}