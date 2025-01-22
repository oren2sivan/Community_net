import subprocess
import os
import json
import socket
import threading
class IPFSCommands:
    def __init__(self,client_socket):
        # Get the correct path using environment variable
        self.ipfs_path = os.path.join(os.environ['USERPROFILE'], 'ipfs_setup', 'kubo')
        self.client_socket=client_socket
        self.remote_ip, remote_port = self.client_socket.getpeername()

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
                self.client_socket.send(self.peer_id.encode())
                print(f"Sent peer ID to server: {self.peer_id}")
                break
            


    def add_bootsrap(self):
        data=self.client_socket.recv(1024).decode()
        data=json.loads(data)
        peer_id=data.get("peer_id")
        full_command = f'ipfs bootstrap add "{peer_id}"'
        print(f"the requested peer id is {peer_id}")
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        print(result)



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
                # Prepend 'ipfs' to the command
                full_command = f"ipfs {command}"
                result = subprocess.run(full_command, shell=True, capture_output=True, text=False)
                
                # Decode stdout and stderr safely
                if result.stdout:
                    output = result.stdout.decode('utf-8', errors='replace')
                    print( output)
                if result.stderr:
                    error_output = result.stderr.decode('utf-8', errors='replace')
                    print("Error:", error_output)
                    
            except Exception as e:
                print(f"Error executing command: {str(e)}")

