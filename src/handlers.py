from . import utils
from .responses import prepare_response
from pathlib import Path

def handle_connection(conn, directory):

    while True:
        # read the request and isolate its components
        data = conn.recv(1024).decode()

        if not data:
            break

        headers = utils.get_headers(data)
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


def handle_get(endpoint, directory, user_agent, compression_scheme):

    # check if the compression scheme is supported
    compression_scheme = utils.validate_compression(compression_scheme)

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