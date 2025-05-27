import argparse


SUPPORTED_ENCODINGS = {
    "gzip"
}



def get_headers(request_data):
    
    headers = {}
    lines = request_data.split("\r\n")

    # iterate through the request line by line to break apart the headers and their values
    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
    
    return headers

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str)
    return parser.parse_args()


def validate_compression(compression):
    
    # check for empty compression list
    if not compression:
        return []
    
    return [c for c in compression if c in SUPPORTED_ENCODINGS]