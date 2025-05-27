import socket
import threading
from src.utils import parse_args
from src.handlers import handle_connection


def main():

    # parse args to extract necessary data i.e. directories
    args = parse_args()
    directory = args.directory


    # creates a TCP socket server bound to IP localhost and port 4221
    server_socket = socket.create_server(("localhost", 4221))   
    server_socket.settimeout(1.0)         
    
    print("Server is active")

    try:
        
        # use while loop to handle multiple requests
        while True:

            try:

                # listen for incoming connection and return connection_socket and address
                connection_socket, addr = server_socket.accept()

                # threading in order to accept multiple connections concurrently
                thread = threading.Thread(target=handle_connection, args=(connection_socket, directory), daemon=True)
                thread.start()

            except socket.timeout:
                pass

    except KeyboardInterrupt:
        print("Shutting down server...")
        server_socket.close()






if __name__ == "__main__":
    main()
