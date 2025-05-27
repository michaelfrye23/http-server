import gzip

STATUS_TEXT = {
    200: "OK",
    201: "Created",
    404: "Not Found",
    400: "Bad Request"
}


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



    
    