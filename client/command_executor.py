import subprocess
import os
import json
import socket
import threading
import ast

class IPFSCommands:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.peer_id = None  # Initialize peer_id
        
        # Get the correct path using environment variable
        self.ipfs_path = os.path.join(os.environ['USERPROFILE'], 'ipfs_setup', 'kubo')
        
        # Get IP address more reliably
        self.remote_ip = self.get_local_ip()
        
        print(f"IPFS Path: {self.ipfs_path}")
        print(f"Remote IP: {self.remote_ip}")
        
        # Verify IPFS path exists
        if not os.path.exists(self.ipfs_path):
            raise FileNotFoundError(f"IPFS path not found: {self.ipfs_path}")
            
        # Change the working directory to where ipfs command is available
        os.chdir(self.ipfs_path)

    def get_local_ip(self):
        """Get local IP address more reliably"""
        try:
            # Create a socket connection to an external server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google's DNS server
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            print(f"Error getting IP address: {e}")
            # Fallback to hostname method
            return socket.gethostbyname(socket.gethostname())

    def inform_server(self):
        try:
            print("Getting IPFS ID...")
            full_command = "ipfs id"
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
            
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
            print(f"Sent peer ID to server: {self.peer_id}")
            
        except Exception as e:
            print(f"Error in inform_server: {e}")
            raise

    def add_bootsrap(self):
        try:
            data = self.client_socket.recv(1024).decode()
            data = json.loads(data)
            peer_id = data.get("peer_id")
            
            if not peer_id:
                raise ValueError("No peer_id received from server")
                
            full_command = f'ipfs bootstrap add "{peer_id}"'
            print(f"Adding bootstrap peer: {peer_id}")
            
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Bootstrap add failed: {result.stderr}")
                
            print("Bootstrap peer added successfully")
            
        except Exception as e:
            print(f"Error in add_bootstrap: {e}")
            raise

    def add_file_to_server(self, file_hash, file_name):
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
            print("Sent file credentials to server")
            
        except Exception as e:
            print(f"Error in add_file_to_server: {e}")
            raise

    def available_files(self):
        try:
            self.client_socket.send(json.dumps({"command": "files-list"}).encode())
            files_list = self.client_socket.recv(4096).decode()
            file_list = ast.literal_eval(files_list)
            
            if not file_list:
                print("No files available")
                self.files = {}
                return
            
            self.files = {file_hash: file_name.strip() for file_name, file_hash in file_list}    

            for index, (file_name, file_hash) in enumerate(file_list):
                print(f"File {index}:")
                print(f"  Name: {file_name.strip()}")
                print(f"  Hash: {file_hash}")
                
        except Exception as e:
            print(f"Error in available_files: {e}")
            raise

    def format_file(self,file_name,file_hash):
        files_locally=subprocess.run("dir",shell=True,capture_output=True,text=True)
        files_locally_names=files_locally.stdout
        if file_hash in files_locally_names:
            change_name=subprocess.run(f"ren {file_hash} {file_name}",shell=True,capture_output=True,text=True)
            move_file=subprocess.run(f"move {file_name} %USERPROFILE%/Downloads",shell=True,capture_output=True,text=True)

    def execute_command(self):
        try:
            self.inform_server()
            print("Starting commander")
            
            bootstrap_thread = threading.Thread(target=self.add_bootsrap)
            bootstrap_thread.start()
            
            while True:
                command = input("command (or 'shutdown'): ").strip()
                
                if not command:
                    continue
                    
                if command.lower() == 'shutdown':
                    subprocess.run("ipfs shutdown", shell=True, capture_output=True)
                    break
                
                try:
                    if command.lower() == 'files-list':
                        self.available_files()
                    
                    else:
                        full_command = f"ipfs {command}"
                        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
                        
                        if result.stdout:
                            output = result.stdout
                            print(output)
                            
                            # Handle file addition
                            if command.lower().startswith("add"):
                                parts = output.split(" ")
                                if len(parts) >= 3:
                                    file_hash = parts[1]
                                    file_name = parts[2]
                                    self.add_file_to_server(file_hash, file_name)
                            elif command.lower().startswith("get"):
                                file_hash=command.split(" ")[1]
                                file_name=self.files[file_hash]
                                self.format_file(file_name,file_hash)
                                    
                        if result.stderr:
                            print("Error:", result.stderr)
                            
                except Exception as e:
                    print(f"Error executing command '{command}': {e}")
                    
        except Exception as e:
            print(f"Error in execute_command: {e}")
            raise


'''
import subprocess
import os
import json
import socket
import threading
import ast
class IPFSCommands:
    def __init__(self,client_socket):
        # Get the correct path using environment variable
        self.ipfs_path = os.path.join(os.environ['USERPROFILE'], 'ipfs_setup', 'kubo')
        self.client_socket=client_socket
        self.remote_ip = socket.gethostbyname(socket.gethostname())
        print(f"Initialized with IP: {self.remote_ip}")

        # Change the working directory to where ipfs command is available
        os.chdir(self.ipfs_path)

    

    def inform_server(self):
        full_command = "ipfs id"
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        output=result.stdout
        parsed_data=json.loads(output)
        addresses = parsed_data.get("Addresses", [])
        for id in addresses:
            if self.remote_ip in id:
                self.peer_id=id
                #self.client_socket.send(self.peer_id.encode())
                #print(f"Sent peer ID to server: {self.peer_id}")
                break

        message={"command":"add-peer-id","peer-id":self.peer_id}
        json_message=json.dumps(message)
        self.client_socket.send(json_message.encode())
        print(f"Sent peer ID to server: {self.peer_id}")
            


    def add_bootsrap(self):
        data=self.client_socket.recv(1024).decode()
        data=json.loads(data)
        peer_id=data.get("peer_id")
        full_command = f'ipfs bootstrap add "{peer_id}"'
        print(f"the requested peer id is {peer_id}")
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        print(result)

    def add_file_to_server(self,file_hash,file_name):
        
        message={"command":"add-file","peer-id":self.peer_id,"file-hash":file_hash,"file-name":file_name}
        json_message=json.dumps(message)
        self.client_socket.send(json_message.encode())
        print("sent file creds to server")
        
    def available_files(self):
        self.client_socket.send(json.dumps({"command": "files-list"}).encode())
        files_list=self.client_socket.recv(4096)
        files_list=files_list.decode()
        file_list = ast.literal_eval(files_list)
        for index, (file_name, file_hash) in enumerate(file_list):
            print(f"File {index}:")
            print(f"  Name: {file_name.strip()}")
            print(f"  Hash: {file_hash}")

    def execute_command(self):
        self.inform_server()
        print("starting commander")
        bootsrap_thread=threading.Thread(target=self.add_bootsrap)
        bootsrap_thread.start()
        while True:
            command = input("command (or 'shutdown'): ")
            
            if command.lower() == 'shutdown':
                full_command = f"ipfs {command}"
                result = subprocess.run(full_command, shell=True, capture_output=True, text=False)


                break
            

            try:
                if command.lower() == 'files-list':
                    #self.client_socket.send(json.dumps({"command": "files-list"}).encode())
                    #files_list=self.client_socket.recv(4096)
                    #print(files_list)
                    self.available_files()
                else:
                    full_command = f"ipfs {command}"
                    result = subprocess.run(full_command, shell=True, capture_output=True, text=False)
                
                    if result.stdout:
                        output = result.stdout.decode('utf-8', errors='replace')
                        print( output)
                        if command.lower().split(" ")[0]=="add":
                            file_name=output.split(" ")[2]
                            file_hash=output.split(" ")[1]
                            self.add_file_to_server(file_hash,file_name)
                    if result.stderr:
                        error_output = result.stderr.decode('utf-8', errors='replace')
                        print("Error:", error_output)
                    
            except Exception as e:
                print(f"Error executing command: {str(e)}")

'''