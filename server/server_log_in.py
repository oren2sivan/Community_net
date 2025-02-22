import socket
import threading
import mongo_setup
import json
class Server:
    

    def __init__(self,ip):

        self.ip = ip 
        self.clients_list=[]
        self.users_collection=mongo_setup.connect_mongo_db_users()

        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip,52128))
        self.server.listen(5)
        print("server running and listening for connections")
        
        self.accept_connections()
    

    def accept_connections(self):
        while True:
            client_socket,addr=self.server.accept()

            print(f"accepted connection from  {addr}")
            self.clients_list.append((client_socket,addr))
            print(self.clients_list)

            thread1=threading.Thread(target=self.authenticate_log_in, args=(client_socket,addr))        
            thread1.start()

    def commns_with_client(self,client_socket):
        while True:
            data=client_socket.recv(1024).decode()
            data=json.loads(data)
            command=data.get("command")
            if command=="add-file":
                file_name=data.get("file-name")
                file_hash=data.get("file-hash")
                peer_id=data.get("peer-id")
                mongo_setup.add_file(peer_id,file_hash,file_name)
            elif command=="files-list":
                client_socket.sendall(str(self.available_files()).encode("utf-8"))
    
    def add_daemon_to_db(self,client_socket):
        try:
            data=client_socket.recv(1024).decode()
            data=json.loads(data)
            peer_id=data.get("peer-id")

            print(f"Received peer ID: {peer_id}")
            data={"peer_id":peer_id}
            mongo_setup.add_daemon_to_mongo(data)
            print("Added peer ID to DB immediately.")
            self.inform_users_bootstrap(peer_id)
            self.commns_with_client(client_socket)
        except Exception as e:
            print(f"Error in add_daemon_to_db: {e}")

    def inform_users_bootstrap(self,peer_id):
        data={"command":"add_bootstrap","peer_id":peer_id}
        data=json.dumps(data)
        for client_socket in self.clients_list:
            client_socket[0].send(data.encode())
            print(f"sent inform to: {client_socket[1]}")
            print(data)

    def send_message(self, client_socket, message,addr):
        try:
            client_socket.sendall(message.encode())
        except:
            print(f"Error sending message to client {client_socket}")
            self.clients_list.remove((client_socket, addr))
            client_socket.close()   

    def authenticate_log_in(self, client_socket, addr):
        while True:
            print("starting authentication")
            data=client_socket.recv(1024).decode()
            print(f"received message from {addr}: {data}")
            message=json.loads(data)
            username=message.get("username")
            password=message.get("password")
            user=self.users_collection.find_one({"username":username,"password":password})
            if user:
                self.send_message(client_socket, "success_log_in", addr)
                print(f"sent success message")
                self.add_daemon_to_db(client_socket)
                break
            
            else:
                print(f"Client {addr} failed to log in")
                self.send_message(client_socket, "failed_log_in", addr)
            
    def available_files(self):
        file_list=mongo_setup.get_files_available()
        return file_list

exm=Server("0.0.0.0")