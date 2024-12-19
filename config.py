import os

SERVER_HOST = "localhost"
SERVER_PORT = 5000
BUFFER_SIZE = 4096
SERVER_FILES_DIR =SERVER_FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_files")

# Ensure the server files directory exists
os.makedirs(SERVER_FILES_DIR, exist_ok=True)

# Maximum number of concurrent connections
MAX_CONNECTIONS = 10

# Timeout for socket operations (in seconds)
SOCKET_TIMEOUT = 60

# File transfer chunk size (in bytes)
CHUNK_SIZE = 8192

# Maximum file size for upload (in bytes, default 1GB)
MAX_UPLOAD_SIZE = 1024 * 1024 * 1024

# Allowed file extensions (empty list means all extensions are allowed)
ALLOWED_EXTENSIONS = [".txt", ".pdf", ".jpg", ".png", ".zip"]

# Enable secure transfers (use SSL/TLS)
USE_SSL = False

# SSL certificate and key files (only used if USE_SSL is True)
SSL_CERT_FILE = "server.crt"
SSL_KEY_FILE = "server.key"

file="error_handling.py"
import tkinter as tk
from tkinter import messagebox
import os
from config import MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS

def handle_error(parent, title, message):
    messagebox.showerror(title, message, parent=parent)

def validate_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    if file_size > MAX_UPLOAD_SIZE:
        raise ValueError(f"File size exceeds maximum allowed size of {MAX_UPLOAD_SIZE} bytes")
    
    _, file_extension = os.path.splitext(file_path)
    if ALLOWED_EXTENSIONS and file_extension.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File extension {file_extension} is not allowed")

def validate_checksum(file_path, received_checksum):
    import hashlib
    
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    
    calculated_checksum = file_hash.hexdigest()
    if calculated_checksum != received_checksum:
        raise ValueError("File checksum validation failed")

def log_error(error_message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"{error_message}\n")

def handle_connection_error(parent, retry_function):
    result = messagebox.askretrycancel(
        "Connection Error",
        "Failed to connect to the server. Would you like to retry?",
        parent=parent
    )
    if result:
        retry_function()
    else:
        parent.quit()

def handle_transfer_error(parent, error_message):
    messagebox.showerror("Transfer Error", error_message, parent=parent)
    log_error(error_message)

