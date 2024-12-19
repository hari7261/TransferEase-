import os
import socket
import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from gui_styles import apply_styles
from file_transfer import send_file, receive_file
from config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
from error_handling import handle_error, validate_file # type: ignore

class ClientGUI:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer Client")
        apply_styles(master)

        self.create_widgets()
        self.client_socket = None
        self.connect_to_server()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=BOTH, expand=YES)

        # Server Files
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

        ttk.Button(btn_frame, text="Upload File", command=self.upload_file).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Download File", command=self.download_file).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Files", command=self.refresh_files).pack(side=LEFT, padx=5)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=X, padx=5, pady=5)

        # Status Log
        log_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="10")
        log_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(side=LEFT, fill=BOTH, expand=YES)

        log_scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            self.log("Connected to server")
            self.refresh_files()
        except Exception as e:
            handle_error(self, "Connection Error", f"Failed to connect to server: {str(e)}")

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.client_socket.send("UPLOAD".encode())
                filename = os.path.basename(file_path)
                self.client_socket.send(filename.encode())
                send_file(self.client_socket, file_path, self.update_progress)
                self.log(f"File '{filename}' uploaded successfully")
                self.refresh_files()
            except Exception as e:
                handle_error(self, "Upload Error", f"Failed to upload file: {str(e)}")

    def download_file(self):
        selected = self.file_list.curselection()
        if selected:
            filename = self.file_list.get(selected[0])
            save_path = filedialog.asksaveasfilename(defaultextension="", initialfile=filename)
            if save_path:
                try:
                    self.client_socket.send("DOWNLOAD".encode())
                    self.client_socket.send(filename.encode())
                    response = self.client_socket.recv(BUFFER_SIZE).decode()
                    if response == "OK":
                        receive_file(self.client_socket, save_path, self.update_progress)
                        self.log(f"File '{filename}' downloaded successfully")
                    else:
                        self.log(f"File '{filename}' not found on server")
                except Exception as e:
                    handle_error(self, "Download Error", f"Failed to download file: {str(e)}")

    def refresh_files(self):
        try:
            self.client_socket.send("LIST".encode())
            file_list = self.client_socket.recv(BUFFER_SIZE).decode()
            self.file_list.delete(0, tk.END)
            for file in file_list.split("\n"):
                self.file_list.insert(tk.END, file)
        except Exception as e:
            handle_error(self, "Refresh Error", f"Failed to refresh file list: {str(e)}")

    def update_progress(self, progress):
        self.progress_var.set(progress)
        self.master.update_idletasks()

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = ttkb.Window(themename="cosmo")
    client_gui = ClientGUI(root)
    root.mainloop()

