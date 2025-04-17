
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, Listbox, Frame, Label, Button, Entry, StringVar, Radiobutton, Text, Scrollbar
import json
import socket
import threading
import os
import subprocess
import sys
import time
import hashlib
import ast
from tkinter import font as tkfont

# Define color theme constants
LIGHT_BLUE = "#e6f2ff"
MEDIUM_BLUE = "#99ccff" 
DARK_BLUE = "#3399ff"
TEXT_COLOR = "#333333"
BUTTON_BG = "#66b3ff"
BUTTON_ACTIVE_BG = "#3399ff"

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("IPFS Private Network Client")
        self.root.geometry("450x350")  # Larger window size
        self.root.configure(bg=LIGHT_BLUE)
        
        # Set custom fonts
        self.title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Arial", size=12)
        self.button_font = tkfont.Font(family="Arial", size=12, weight="bold")

        # Get Server IP
        self.server_ip = simpledialog.askstring("Server IP", "Enter server IP:")
        if not self.server_ip:
            messagebox.showerror("Error", "Server IP is required")
            root.destroy()
            return

        # Connect to Server
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, 52128))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            root.destroy()
            return

        # Main frame with padding
        main_frame = Frame(root, bg=LIGHT_BLUE, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        Label(main_frame, text="IPFS Private Network", font=self.title_font, bg=LIGHT_BLUE, fg=DARK_BLUE).pack(pady=(10, 20))
        
        # Username Field
        Label(main_frame, text="Username:", font=self.label_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(pady=(10, 5), anchor="w")
        self.username_entry = Entry(main_frame, font=self.label_font, width=30, bg="white", fg=TEXT_COLOR)
        self.username_entry.pack(pady=5, ipady=3, fill="x")

        # Password Field
        Label(main_frame, text="Password:", font=self.label_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(pady=(10, 5), anchor="w")
        self.password_entry = Entry(main_frame, show="*", font=self.label_font, width=30, bg="white", fg=TEXT_COLOR)
        self.password_entry.pack(pady=5, ipady=3, fill="x")

        # Login Button
        self.login_button = Button(
            main_frame, 
            text="Login", 
            command=self.send_to_server,
            font=self.button_font,
            bg=BUTTON_BG,
            fg="white",
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground="white",
            padx=20,
            pady=5,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.login_button.pack(pady=20)

    def send_to_server(self):
        """Send login credentials to the server."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        creds = json.dumps({"username": username, "password": password})
        
        try:
            self.client_socket.sendall(creds.encode())  # Send credentials to server
            threading.Thread(target=self.wait_for_response, daemon=True).start()  # Wait for response in a separate thread
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to send data: {e}")

    def wait_for_response(self):
        """Wait for the server's response asynchronously."""
        try:
            response = self.client_socket.recv(1024).decode()
            if response == "success_log_in":
                messagebox.showinfo("Login Successful", "You have successfully logged in!")
                self.root.withdraw()  # Hide login window instead of destroying
                SetupWindow(self.client_socket, self.root, self.server_ip)  # Pass server IP
            elif response == "failed_log_in":
                messagebox.showerror("Login Failed", "Invalid credentials. Try again.")
            else:
                messagebox.showerror("Error", f"Unexpected server response: {response}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to receive response: {e}")

class SetupWindow:
    def __init__(self, client_socket, root, remote_ip):
        self.client_socket = client_socket
        self.root = root
        self.remote_ip = remote_ip
        
        # Set custom fonts
        self.title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        self.heading_font = tkfont.Font(family="Arial", size=14, weight="bold")
        self.label_font = tkfont.Font(family="Arial", size=12)
        self.button_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.log_font = tkfont.Font(family="Consolas", size=10)
        
        self.window = tk.Toplevel(root)
        self.window.title("IPFS Setup")
        self.window.geometry("600x500")  # Larger window size
        self.window.configure(bg=LIGHT_BLUE)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Title
        Label(self.window, text="IPFS Network Setup", font=self.title_font, bg=LIGHT_BLUE, fg=DARK_BLUE).pack(pady=(20, 30))
        
        # Setup type selection
        self.setup_frame = Frame(self.window, bg=LIGHT_BLUE, padx=30, pady=20)
        self.setup_frame.pack(fill="both", expand=True)
        
        Label(self.setup_frame, text="Choose Setup Option:", font=self.heading_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(pady=(0, 15), anchor="w")
        
        self.setup_type = StringVar()
        self.setup_type.set("daemon")
        
        setup_options_frame = Frame(self.setup_frame, bg=LIGHT_BLUE)
        setup_options_frame.pack(fill="x", pady=5)
        
        Radiobutton(
            setup_options_frame, 
            text="Daemon Only (IPFS already installed)", 
            variable=self.setup_type, 
            value="daemon",
            font=self.label_font,
            bg=LIGHT_BLUE,
            fg=TEXT_COLOR,
            selectcolor=MEDIUM_BLUE
        ).pack(anchor="w", padx=10, pady=8)
        
        Radiobutton(
            setup_options_frame, 
            text="Total Setup (Install IPFS and dependencies)", 
            variable=self.setup_type, 
            value="total",
            font=self.label_font,
            bg=LIGHT_BLUE,
            fg=TEXT_COLOR,
            selectcolor=MEDIUM_BLUE
        ).pack(anchor="w", padx=10, pady=8)
        
        # Community ID Entry
        Label(self.setup_frame, text="Community ID (Password):", font=self.heading_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(pady=(25, 10), anchor="w")
        
        community_id_frame = Frame(self.setup_frame, bg=LIGHT_BLUE)
        community_id_frame.pack(fill="x", pady=5)
        
        self.community_id = Entry(
            community_id_frame, 
            show="*", 
            font=self.label_font,
            bg="white",
            fg=TEXT_COLOR,
            width=30
        )
        self.community_id.pack(fill="x", ipady=5)
        
        # Start Button
        Button(
            self.setup_frame, 
            text="Start IPFS", 
            command=self.start_ipfs_setup,
            font=self.button_font,
            bg=BUTTON_BG,
            fg="white",
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground="white",
            padx=20,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(pady=30)
        
        # Log window (initially hidden)
        self.log_frame = Frame(self.window, bg=LIGHT_BLUE, padx=20, pady=20)
        
        Label(self.log_frame, text="Setup Progress:", font=self.heading_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        
        # Create a frame for the text widget with a border
        text_container = Frame(self.log_frame, bd=2, relief=tk.SUNKEN)
        text_container.pack(fill="both", expand=True)
        
        # Add scrollbar to the text output
        scrollbar = Scrollbar(text_container)
        scrollbar.pack(side="right", fill="y")
        
        self.log_text = Text(
            text_container, 
            height=15, 
            width=60,
            wrap="word", 
            yscrollcommand=scrollbar.set,
            font=self.log_font,
            bg="white",
            fg=TEXT_COLOR
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

    def on_close(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            try:
                self.client_socket.close()
            except:
                pass
            self.root.destroy()
            sys.exit()

    def log_message(self, message):
        """Add message to log window."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)  # Scroll to the end
        self.window.update()  # Update GUI

    def start_ipfs_setup(self):
        """Start the IPFS setup process based on selected option."""
        setup_type = self.setup_type.get()
        community_id = self.community_id.get()
        
        if not community_id:
            messagebox.showerror("Error", "Please enter a Community ID")
            return
        
        # Show log frame
        self.setup_frame.pack_forget()
        self.log_frame.pack(fill="both", expand=True)
        
        # Run setup in a separate thread
        threading.Thread(target=self.run_setup, args=(setup_type, community_id), daemon=True).start()

    def run_setup(self, setup_type, community_id):
        """Run the appropriate setup based on selection."""
        self.log_message(f"Starting {setup_type} setup...")
        
        try:
            # Handle paths for both development and PyInstaller environments
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_path = sys._MEIPASS
                script_dir = base_path
            else:
                # Running in development environment
                script_dir = os.path.dirname(os.path.abspath(__file__))
                base_path = os.path.dirname(script_dir)
            
            self.log_message(f"Base path: {base_path}")
            self.log_message(f"Script directory: {script_dir}")
            
            # Define paths
            dependencies_bat = os.path.join(base_path, "config", "dependencies-1.bat")
            ipfs_config_bat = os.path.join(base_path, "config", "ipfs_config.bat")
            
            self.log_message(f"Dependencies path: {dependencies_bat}")
            self.log_message(f"IPFS config path: {ipfs_config_bat}")
            
            if setup_type == "total":
                # Run dependencies batch file
                self.log_message("Running dependencies installation...")
                subprocess.run(dependencies_bat, shell=True, check=True)
                self.log_message("Dependencies installed successfully.")
            
            # Generate swarm key
            self.log_message("Generating swarm key...")
            self.generate_swarm_key(community_id)
            
            # Run IPFS config batch file
            self.log_message("Configuring IPFS for private network...")
            subprocess.Popen(ipfs_config_bat, shell=True)
            
            self.log_message("Waiting for IPFS daemon to start...")
            time.sleep(6)
            
            self.log_message("Setup completed successfully!")
            self.log_message("Starting command executor...")
            
            # Launch command executor window
            self.window.after(0, lambda: self.open_command_executor())
            
        except Exception as e:
            self.log_message(f"Error during setup: {e}")
            messagebox.showerror("Setup Error", f"Failed to complete setup: {e}")

    def generate_swarm_key(self, password):
        """Generate swarm key from the community ID."""
        try:
            key = hashlib.sha256(password.encode()).hexdigest()
            swarm_key_content = f"/key/swarm/psk/1.0.0/\n/base16/\n{key}"
            
            # Get the expanded %USERPROFILE% path
            ipfs_path = os.path.expandvars("%USERPROFILE%\\.ipfs")
            
            # Create .ipfs directory if it doesn't exist
            if not os.path.exists(ipfs_path):
                os.makedirs(ipfs_path)
            
            # Write swarm key directly to the proper location
            swarm_key_path = os.path.join(ipfs_path, "swarm.key")
            with open(swarm_key_path, "w") as f:
                f.write(swarm_key_content)
                
            self.log_message(f"Swarm key generated successfully at {swarm_key_path}")
        except Exception as e:
            self.log_message(f"Error generating swarm key: {e}")
            raise

    def open_command_executor(self):
        """Open the command executor window."""
        self.window.withdraw()  # Hide setup window
        IPFSCommandExecutor(self.client_socket, self.root, self.remote_ip)  # Pass remote_ip



class IPFSCommandExecutor:
    def __init__(self, client_socket, root, remote_ip):
        self.client_socket = client_socket
        self.remote_ip = remote_ip
        self.peer_id = None
        self.files = {}
        
        # Set custom fonts
        self.title_font = tkfont.Font(family="Arial", size=16, weight="bold")
        self.heading_font = tkfont.Font(family="Arial", size=14, weight="bold")
        self.label_font = tkfont.Font(family="Arial", size=12)
        self.button_font = tkfont.Font(family="Arial", size=11, weight="bold")
        self.log_font = tkfont.Font(family="Consolas", size=10)
        
        self.window = tk.Toplevel(root)
        self.window.title("IPFS Command Executor")
        self.window.geometry("900x700")  # Larger window size
        self.window.configure(bg=LIGHT_BLUE)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Title
        Label(self.window, text="IPFS Command Center", font=self.title_font, bg=LIGHT_BLUE, fg=DARK_BLUE).pack(pady=(20, 30))
        
        # Main frame
        main_frame = Frame(self.window, bg=LIGHT_BLUE)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Command output area
        output_frame = Frame(main_frame, bg=LIGHT_BLUE)
        output_frame.pack(fill="both", expand=True, pady=5)
        
        Label(output_frame, text="Command Output:", font=self.heading_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        
        # Create a frame for the text widget with a border
        text_frame = Frame(output_frame, bd=2, relief=tk.SUNKEN)
        text_frame.pack(fill="both", expand=True)
        
        # Add scrollbar to the text output
        scrollbar = Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.output_text = Text(
            text_frame, 
            height=20, 
            wrap="word", 
            yscrollcommand=scrollbar.set,
            font=self.log_font,
            bg="white",
            fg=TEXT_COLOR
        )
        self.output_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.output_text.yview)
        
        # Command input area
        input_frame = Frame(main_frame, bg=LIGHT_BLUE, pady=15)
        input_frame.pack(fill="x")
        
        Label(input_frame, text="Enter IPFS Command:", font=self.heading_font, bg=LIGHT_BLUE, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        
        command_entry_frame = Frame(input_frame, bg=LIGHT_BLUE)
        command_entry_frame.pack(fill="x", pady=5)
        
        self.command_entry = Entry(
            command_entry_frame, 
            width=50, 
            font=self.label_font,
            bg="white",
            fg=TEXT_COLOR
        )
        self.command_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.command_entry.bind("<Return>", lambda event: self.execute_ipfs_command())
        
        # Button area (using a separate frame for better organization)
        button_frame = Frame(main_frame, bg=LIGHT_BLUE, pady=10)
        button_frame.pack(fill="x")
        
        # Style for all buttons
        button_style = {
            "font": self.button_font,
            "bg": BUTTON_BG,
            "fg": "white",
            "activebackground": BUTTON_ACTIVE_BG,
            "activeforeground": "white",
            "padx": 15,
            "pady": 8,
            "cursor": "hand2",
            "relief": tk.RAISED,
            "bd": 2
        }
        
        Button(
            button_frame, 
            text="Execute", 
            command=self.execute_ipfs_command,
            **button_style
        ).pack(side="left", padx=10)
        
        Button(
            button_frame, 
            text="List Files", 
            command=self.list_files,
            **button_style
        ).pack(side="left", padx=10)
        
        Button(
            button_frame, 
            text="Shutdown IPFS", 
            command=self.shutdown_ipfs,
            **button_style
        ).pack(side="left", padx=10)
        
        # Start the IPFS peer connection process
        threading.Thread(target=self.initialize_ipfs, daemon=True).start()
    
    def on_close(self):
        """Handle window close event."""
        if messagebox.askokcancel("Quit", "Do you want to quit the application? This will also shut down IPFS daemon."):
            try:
                # Shutdown IPFS daemon
                ipfs_path = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo\\ipfs")
                kubo_dir = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo")
                subprocess.run(f'"{ipfs_path}" shutdown', shell=True, cwd=kubo_dir)
                self.client_socket.close()
            except:
                pass
            self.window.master.destroy()
            sys.exit()
    
    def log_message(self, message):
        """Add message to output text."""
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.window.update()
    
    def initialize_ipfs(self):
        """Initialize IPFS connection and inform server."""
        try:
            self.log_message("Initializing IPFS connection...")
            self.inform_server()
            self.log_message("Adding bootstrap peer...")
            self.add_bootstrap()
            self.log_message("IPFS initialized successfully!")
            
            # Inform client we're connected
            self.client_socket.send(json.dumps({"command": "client_connected"}).encode())
            
        except Exception as e:
            self.log_message(f"Error initializing IPFS: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize IPFS: {e}")
    
    def inform_server(self):
        """Get IPFS ID and inform server."""
        try:
            self.log_message("Getting IPFS ID...")
            ipfs_path = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo\\ipfs")
            kubo_dir = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo")
            
            result = subprocess.run(f'"{ipfs_path}" id', shell=True, capture_output=True, text=True, cwd=kubo_dir)
            
            if result.returncode != 0:
                raise Exception(f"IPFS ID command failed: {result.stderr}")
            
            output = result.stdout
            parsed_data = json.loads(output)
            addresses = parsed_data.get("Addresses", [])
            
            # Find matching peer ID
            peer_id_found = False
            for addr in addresses:
                if self.remote_ip in addr:
                    self.peer_id = addr
                    peer_id_found = True
                    break
            
            if not peer_id_found:
                # If no exact IP match, take the first local address as fallback
                for addr in addresses:
                    if any(local_prefix in addr for local_prefix in ['/ip4/127.', '/ip4/192.168.', '/ip4/10.']):
                        self.peer_id = addr
                        peer_id_found = True
                        break
            
            if not peer_id_found:
                raise Exception("No suitable peer ID found in IPFS addresses")
            
            message = {
                "command": "add-peer-id",
                "peer-id": self.peer_id
            }
            json_message = json.dumps(message)
            self.client_socket.send(json_message.encode())
            self.log_message(f"Sent peer ID to server: {self.peer_id}")
            
        except Exception as e:
            self.log_message(f"Error in inform_server: {e}")
            raise
    
    def add_bootstrap(self):
        """Add bootstrap peer from server."""
        try:
            data = self.client_socket.recv(1024).decode()
            data = json.loads(data)
            peer_id = data.get("peer_id")
            
            if not peer_id:
                raise ValueError("No peer_id received from server")
                
            ipfs_path = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo\\ipfs")
            kubo_dir = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo")
            full_command = f'"{ipfs_path}" bootstrap add "{peer_id}"'
            self.log_message(f"Adding bootstrap peer: {peer_id}")
            
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True, cwd=kubo_dir)
            if result.returncode != 0:
                raise Exception(f"Bootstrap add failed: {result.stderr}")
                
            self.log_message("Bootstrap peer added successfully")
            
        except Exception as e:
            self.log_message(f"Error in add_bootstrap: {e}")
            raise

    def add_file_to_server(self, file_hash, file_name):
        """Add file information to server with improved error handling."""
        try:
            if not self.peer_id:
                raise ValueError("Peer ID not initialized")
        
            # Validate inputs
            if not file_hash or not file_name:
                self.log_message("Invalid file hash or name")
                return
        
            message = {
                "command": "add-file",
                "peer-id": self.peer_id,
                "file-hash": file_hash,
                "file-name": file_name
            }
        
            # Send file information
            json_message = json.dumps(message)
            self.client_socket.send(json_message.encode())
        
            # Log success
            self.log_message(f"Sent file credentials: {file_name} (Hash: {file_hash})")
        
        except Exception as e:
            error_message = f"Error in add_file_to_server: {e}"
            self.log_message(error_message)        
    
    '''
    def add_file_to_server(self, file_hash, file_name):
        """Add file information to server."""
        try:
            if not self.peer_id:
                raise ValueError("peer_id not initialized")
                
            message = {
                "command": "add-file",
                "peer-id": self.peer_id,
                "file-hash": file_hash,
                "file-name": file_name
            }
            json_message = json.dumps(message)
            self.client_socket.send(json_message.encode())
            self.log_message("Sent file credentials to server")
            
        except Exception as e:
            self.log_message(f"Error in add_file_to_server: {e}")
    '''
    def list_files(self):
        """List available files from server."""
        try:
            self.client_socket.send(json.dumps({"command": "files-list"}).encode())
            files_list = self.client_socket.recv(4096).decode()
            file_list = ast.literal_eval(files_list)
        
            # Clear previous output
            self.output_text.delete('1.0', tk.END)
        
            if not file_list:
                self.output_text.insert(tk.END, "No files available\n")
                self.files = {}
                return
        
            self.files = {file_hash: file_name.strip() for file_name, file_hash in file_list}    

            for index, (file_name, file_hash) in enumerate(file_list):
                self.output_text.insert(tk.END, f"File {index}:\n")
                self.output_text.insert(tk.END, f"  Name: {file_name.strip()}\n")
                self.output_text.insert(tk.END, f"  Hash: {file_hash}\n")
        
        except Exception as e:
            error_message = f"Error in list_files: {e}"
            self.output_text.insert(tk.END, f"{error_message}\n")
            # Optionally re-raise if you want to propagate the exception
            raise
    ''''
    def list_files(self):
        """List available files from server."""
        try:
            self.client_socket.send(json.dumps({"command": "files-list"}).encode())
            files_list = self.client_socket.recv(4096).decode()
            file_list = ast.literal_eval(files_list)
            
            self.output_text.insert(tk.END, "\n--- Available Files ---\n")
            
            if not file_list:
                self.log_message("No files available")
                self.files = {}
                return
            
            self.files = {file_hash: file_name.strip() for file_name, file_hash in file_list}    

            for index, (file_name, file_hash) in enumerate(file_list):
                self.output_text.insert(tk.END, f"File {index}:\n")
                self.output_text.insert(tk.END, f"  Name: {file_name.strip()}\n")
                self.output_text.insert(tk.END, f"  Hash: {file_hash}\n")
            
            self.output_text.insert(tk.END, "--------------------\n")
            self.output_text.see(tk.END)
                
        except Exception as e:
            self.log_message(f"Error listing files: {e}")
    '''
    def format_file(self, file_name, file_hash):
        """Format and move downloaded file."""
        try:
            # Run dir command from kubo directory
            kubo_dir = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo")
            files_locally = subprocess.run("dir", shell=True, capture_output=True, text=True, cwd=kubo_dir)
            files_locally_names = files_locally.stdout
            
            if file_hash in files_locally_names:
                self.log_message(f"Renaming {file_hash} to {file_name}")
                change_name = subprocess.run(f"ren {file_hash} {file_name}", shell=True, capture_output=True, text=True, cwd=kubo_dir)
                
                self.log_message(f"Moving {file_name} to Downloads folder")
                move_file = subprocess.run(f"move {file_name} %USERPROFILE%\\Downloads", shell=True, capture_output=True, text=True, cwd=kubo_dir)
                
                self.log_message("File processed successfully")
        except Exception as e:
            self.log_message(f"Error formatting file: {e}")
    
    def shutdown_ipfs(self):
        """Shut down IPFS daemon."""
        try:
            self.log_message("Shutting down IPFS daemon...")
            ipfs_path = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo\\ipfs")
            kubo_dir = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo")
            
            result = subprocess.run(f'"{ipfs_path}" shutdown', shell=True, capture_output=True, text=True, cwd=kubo_dir)
            
            if result.returncode == 0:
                self.log_message("IPFS daemon shut down successfully")
            else:
                self.log_message(f"Error shutting down IPFS daemon: {result.stderr}")
        except Exception as e:
            self.log_message(f"Error shutting down IPFS daemon: {e}")
    
    def execute_ipfs_command(self):
        """Execute IPFS command from GUI input."""
        command = self.command_entry.get().strip()
        if not command:
            return
            
        self.command_entry.delete(0, tk.END)
        self.log_message(f"\n> ipfs {command}")
        
        try:
            if command.lower() == 'files-list':
                self.list_files()
            elif command.lower() == 'shutdown':
                self.shutdown_ipfs()
            else:
                # Use the correct path for IPFS
                ipfs_path = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo\\ipfs")
                kubo_dir = os.path.expandvars("%USERPROFILE%\\ipfs_setup\\kubo")
                full_command = f'"{ipfs_path}" {command}'
                
                # Execute the command
                process = subprocess.Popen(
                    full_command, 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=kubo_dir  # Run in kubo directory
                )
                
                stdout, stderr = process.communicate()
                
                if stdout:
                    self.log_message(stdout)
                    
                    # Handle file addition
                    if command.lower().startswith("add"):
                        parts = stdout.split(" ")
                        if len(parts) >= 3:
                            file_hash = parts[1]
                            file_name = parts[2]
                            self.add_file_to_server(file_hash, file_name)
                    elif command.lower().startswith("get"):
                        file_hash = command.split(" ")[1]
                        if file_hash in self.files:
                            file_name = self.files[file_hash]
                            self.format_file(file_name, file_hash)
                        else:
                            self.log_message(f"Warning: File hash {file_hash} not found in known files")
                            
                if stderr:
                    self.log_message(f"Error: {stderr}")
                    
        except Exception as e:
            self.log_message(f"Error executing command '{command}': {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()



