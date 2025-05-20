import socket
import threading
import argparse
from pathlib import Path
import gzip


STATUS_TEXT = {
    200: "OK",
    201: "Created",
    404: "Not Found",
    400: "Bad Request"
}

SUPPORTED_ENCODINGS = {
    "gzip"
}


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


def handle_connection(conn, directory):

    while True:
        # read the request and isolate its components
        data = conn.recv(1024).decode()

        if not data:
            break

        headers = get_headers(data)
        request_line = data.splitlines()[0]
        user_agent = headers.get("User-Agent")
        compression = headers.get("Accept-Encoding")

        body = data.split("\r\n\r\n")[1]
        

        try:

            method, path, _ = request_line.split()

            if method == "GET":
                response = handle_get(path, directory, user_agent, compression)
            elif method == "POST":
                response = handle_post(path, directory, user_agent, body)
            else:
                raise ValueError

        except ValueError:

            response = prepare_response(400, "Bad Request")
        
        
        # send HTTP response
        conn.sendall(response)

        if headers.get("Connection", "").lower() == "close":
            break
        
    conn.close()

def get_headers(request_data):
    
    headers = {}
    lines = request_data.split("\r\n")

    # iterate through the request line by line to break apart the headers and their values
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
    
    return headers


def handle_get(endpoint, directory, user_agent, compression_scheme):

    # check if the compression scheme is supported
    compression_scheme = validate_compression(compression_scheme)

    # default path
    if endpoint == '/':
        response = prepare_response(200, "Welcome!")

    # echo endpoint. repeat the string following '/echo/' in the URL path in the response body
    elif endpoint.startswith("/echo/"):
        echoed_text = endpoint[6:]

        # check if the message to echo is empty
        if not echoed_text.strip():
            echoed_text = "Nothing to echo"

        response = prepare_response(200, echoed_text, compression=compression_scheme)

    # User-Agent endpoint. include the User-Agent in the response body
    elif endpoint == "/user-agent":
        response = prepare_response(200, user_agent)

    # check and retrieve file information
    elif endpoint.startswith("/files/"):
        file_path = Path(directory) / endpoint[7:]
        try:
            file_contents = file_path.read_bytes()
            response = prepare_response(200, file_contents, type="application/octet-stream")
        except FileNotFoundError:
            response = prepare_response(404, "Not Found")

    # if the endpoint dne
    else:
        response = prepare_response(404, "Not Found")

    return response

def handle_post(endpoint, directory, user_agent, body):

    # determine endpoint
    if endpoint.startswith("/files/"):
        file_path = Path(directory) / endpoint[7:]
        file_path.touch()
        
        # determine if the body is text or bytes
        if type(body) is str:
            file_path.write_text(body)
            response = prepare_response(201)
        else:
            file_path.write_bytes(body)
            response = prepare_response(201)

    return response

def prepare_response(status_code, body=None, type="text/plain", compression=None):

    # initialize the response line
    response = f"HTTP/1.1 {status_code} {STATUS_TEXT[status_code]}\r\n"

    if isinstance(body, str):
            body = body.encode()

    if compression:
        if "gzip" in compression:

            body = gzip.compress(body)
            response += "Content-Encoding: gzip\r\n"

    if body is not None:
        response += (
            f"Content-Type: {type}\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
            )

        return response.encode() + body
    
    response += "\r\n"

    

    return response.encode()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str)
    return parser.parse_args()

def validate_compression(compression):
    
    # check for empty compression list
    if not compression:
        return []
    
    return [c for c in compression if c in SUPPORTED_ENCODINGS]
    
    

if __name__ == "__main__":
    main()
