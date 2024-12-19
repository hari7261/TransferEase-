import os
from config import BUFFER_SIZE

def send_file(sock, file_path, progress_callback=None):
    file_size = os.path.getsize(file_path)
    sock.send(str(file_size).encode())
    
    with open(file_path, "rb") as f:
        bytes_sent = 0
        while bytes_sent < file_size:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendall(chunk)
            bytes_sent += len(chunk)
            if progress_callback:
                progress = (bytes_sent / file_size) * 100
                progress_callback(progress)

def receive_file(sock, file_path, progress_callback=None):
    file_size = int(sock.recv(BUFFER_SIZE).decode())
    
    with open(file_path, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            f.write(chunk)
            bytes_received += len(chunk)
            if progress_callback:
                progress = (bytes_received / file_size) * 100
                progress_callback(progress)

