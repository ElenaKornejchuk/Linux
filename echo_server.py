import socket
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

HOST = '127.0.0.1'
PORT = 8081


def parse_request(request_data):
    lines = request_data.split('\r\n')
    if not lines or not lines[0].strip():
        raise ValueError("Empty or malformed request")

    request_line = lines[0]
    parts = request_line.split()
    if len(parts) != 3:
        raise ValueError("Malformed request line")

    method, path, protocol = parts
    headers = {}

    for line in lines[1:]:
        if line == '':
            break
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key] = value

    return method, path, headers


def get_status(path):
    parsed_url = urlparse(path)
    query = parse_qs(parsed_url.query)
    status_code = query.get("status", [200])[0]

    try:
        status_code = int(status_code)
        return HTTPStatus(status_code)
    except (ValueError, KeyError):
        return HTTPStatus.OK
    except Exception:
        return HTTPStatus.INTERNAL_SERVER_ERROR


def handle_client(client_socket, client_address):
    request_data = client_socket.recv(1024).decode('utf-8')
    if not request_data.strip():
        client_socket.close()
        return

    print(f"\n Запрос от клиента {client_address}:\n{request_data}")

    try:
        method, path, headers = parse_request(request_data)
    except ValueError:
        status = HTTPStatus.BAD_REQUEST
        response_body = "400 Bad Request"

        response = f"""HTTP/1.1 {status.value} {status.phrase}
Content-Type: text/plain
Content-Length: {len(response_body)}

{response_body}"""
        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()
        return

    status = get_status(path)

    response_lines = [
        f"Request Method: {method}",
        f"Request Source: {client_address}",
        f"Response Status: {status.value} {status.phrase}",
    ] + [f"{k}: {v}" for k, v in headers.items()]

    response_body = '\n'.join(response_lines)

    response = (
        f"HTTP/1.1 {status.value} {status.phrase}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
        f"\r\n"
        f"{response_body}"
    )

    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Запуск сервера на http://{HOST}:{PORT}")

        while True:
            client_socket, client_address = server_socket.accept()
            handle_client(client_socket, client_address)


if __name__ == '__main__':
    run_server()
