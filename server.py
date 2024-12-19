import os
import socket
import threading
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_styles import apply_styles
from file_transfer import send_file, receive_file
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE, SERVER_FILES_DIR
from error_handling import handle_error, validate_file # type: ignore

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer Server")
        apply_styles(master)

        self.create_widgets()
        self.server_socket = None
        self.clients = []
        self.start_server()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=BOTH, expand=YES)

        # File List
        file_frame = ttk.LabelFrame(main_frame, text="Server Files", padding="10")
        file_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        self.file_list = tk.Listbox(file_frame, height=10)
        self.file_list.pack(side=LEFT, fill=BOTH, expand=YES)

        scrollbar = ttk.Scrollbar(file_frame, orient=VERTICAL, command=self.file_list.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.file_list.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Refresh Files", command=self.refresh_files).pack(side=LEFT, padx=5)

        # Status Log
        log_frame = ttk.LabelFrame(main_frame, text="Server Log", padding="10")
        log_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(side=LEFT, fill=BOTH, expand=YES)

        log_scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        # Performance Monitoring
        perf_frame = ttk.LabelFrame(main_frame, text="Performance", padding="10")
        perf_frame.pack(fill=X, padx=5, pady=5)

        ttk.Label(perf_frame, text="Active Connections:").pack(side=LEFT, padx=5)
        self.active_connections = ttk.Label(perf_frame, text="0")
        self.active_connections.pack(side=LEFT, padx=5)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.server_socket.listen(5)
        self.log(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

    def accept_connections(self):
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.daemon = True
            client_thread.start()
            self.clients.append(client_socket)
            self.update_active_connections()

    def handle_client(self, client_socket, address):
        self.log(f"New connection from {address}")
        while True:
            try:
                command = client_socket.recv(BUFFER_SIZE).decode()
                if command == "UPLOAD":
                    self.handle_upload(client_socket)
                elif command == "DOWNLOAD":
                    self.handle_download(client_socket)
                elif command == "LIST":
                    self.send_file_list(client_socket)
                elif command == "DISCONNECT":
                    break
            except Exception as e:
                self.log(f"Error handling client {address}: {str(e)}")
                break
        client_socket.close()
        self.clients.remove(client_socket)
        self.update_active_connections()
        self.log(f"Connection closed from {address}")

    def handle_upload(self, client_socket):
        filename = client_socket.recv(BUFFER_SIZE).decode()
        file_path = os.path.join(SERVER_FILES_DIR, filename)
        receive_file(client_socket, file_path)
        self.log(f"File '{filename}' uploaded successfully")
        self.refresh_files()

    def handle_download(self, client_socket):
        filename = client_socket.recv(BUFFER_SIZE).decode()
        file_path = os.path.join(SERVER_FILES_DIR, filename)
        if os.path.exists(file_path):
            client_socket.send("OK".encode())
            send_file(client_socket, file_path)
            self.log(f"File '{filename}' downloaded by client")
        else:
            client_socket.send("FILE_NOT_FOUND".encode())
            self.log(f"File '{filename}' not found on server")

    def send_file_list(self, client_socket):
        files = os.listdir(SERVER_FILES_DIR)
        file_list = "\n".join(files)
        client_socket.send(file_list.encode())

    def refresh_files(self):
        self.file_list.delete(0, tk.END)
        files = os.listdir(SERVER_FILES_DIR)
        for file in files:
            self.file_list.insert(tk.END, file)

    def update_active_connections(self):
        self.active_connections.config(text=str(len(self.clients)))

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = ttkb.Window(themename="cosmo")
    server_gui = ServerGUI(root)
    root.mainloop()

