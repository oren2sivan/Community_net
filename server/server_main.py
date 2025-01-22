import socket
import threading
import mongo_setup
#
class Server:
    

    def __init__(self,ip):

        self.ip = ip 
        self.clients_list=[]

        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip,52124))
        self.server.listen(5)
        print("server running and listening for connections")
        self.menu_thread = threading.Thread(target=self.send_message_menu)
        self.menu_thread.start()
        self.accept_connections()
        self.users_collection=mongo_setup.connect_mongo_db_users()
    

    def accept_connections(self):
        while True:
            client_socket,addr=self.server.accept()

            print(f"accepted connection from  {addr}")
            self.clients_list.append((client_socket,addr))
            print(self.clients_list)

            thread1=threading.Thread(target=self.authenticate_log_in, args=(client_socket,addr))        
            thread1.start()



    def send_message_menu(self):
        while True:
            print("\nSelect a client to send a message to:")
            for idx, (client_socket, addr) in enumerate(self.clients_list):
                print(f"{idx}: {addr}")

            try:
                client_idx = int(input("Enter client number (or -1 to exit): "))
                if client_idx == -1:
                    break

                if 0 <= client_idx < len(self.clients_list):
                    client_socket, addr = self.clients_list[client_idx]
                    message = input("Enter the message to send: ")

                    if message == "exit":
                        print("Ending conversation")
                        client_socket.sendall("exit".encode())
                        client_socket.close()
                        self.clients_list.pop(client_idx)

                    else:
                        send_thread = threading.Thread(target=self.send_message, args=(client_socket, message, addr))
                        send_thread.start()
                else:
                    print("Invalid client selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print(f"Error sending message: {e}")


    def send_message(self, client_socket, message,addr):
        try:
            client_socket.sendall(message.encode())
        except:
            print(f"Error sending message to client {client_socket}")
            self.clients_list.remove((client_socket, addr))
            client_socket.close()   

    def authenticate_log_in(self, client_socket, addr):
            while True:
                try:
                    username = client_socket.recv(1024).decode()
                    password = client_socket.recv(1024).decode()
                    user=self.users_collection.find_one({"username":username,"password":password})
                    if user:
                        client_socket.sendall("success_log_in".encode())
                        print(f"sent success message")
                        self.clients_list.remove((client_socket, addr))  
                        client_socket.close()
                        print(f"Client {addr} ended the conversation")
                        
                        break
                    else:
                        print(f"Client {addr} failed to log in")
                except:
                    print(f"Error receiving message from client {addr}")
                    self.clients_list.remove((client_socket, addr))
                    client_socket.close()
                    break



exm=Server("127.0.0.1")

'''
    def recieve_from_client(self, client_socket, addr):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message == "exit":
                    print(f"Client {addr} ended the conversation")
                    self.clients_list.remove((client_socket, addr))  
                    client_socket.close()
                    break
                print(f"Message from {addr}:   {message}")
            except:
                print(f"Error receiving message from client {addr}")
                self.clients_list.remove((client_socket, addr))
                client_socket.close()
                break
'''        


