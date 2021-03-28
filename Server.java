import java.net.ServerSocket;
import java.net.Socket;
import java.io.PrintWriter;
import java.io.BufferedReader;
import java.io.InputStreamReader;

// Remaking this code cause it was shittiest code in my life!
class Client {
	Socket socket;
	String username;
}
public class Server {
	ServerSocket serverSock;
	Socket client;
	static boolean serverAlive = true;

	Server(int port) {
		try
		{
			serverSock = new ServerSocket(port);
		}
		catch(Exception e)
		{
			System.out.println("cannot start server!");
			System.exit(-1);
		}

	}
	
	public static void main(String[] args) {
		Server server = new Server(Integer.parseInt(args[0]));
		System.out.println("Server has started ...");

		server.start();
	}

	public void start() {
		
		while(serverAlive) {
			try
			{
				client = serverSock.accept();
				System.out.printf("client connected! ");
			}
			catch(Exception e)
			{
				System.out.println(e);
				serverAlive = false;
			}
		}
	}
}