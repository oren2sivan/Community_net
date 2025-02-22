import gen_swarm_key
import subprocess
import threading
from command_executor import IPFSCommands
import time
import os
import sys
class setup:
    def __init__(self, setup_type, client_socket):
        self.setup_type = setup_type
        self.client_socket = client_socket
        
        # Handle paths for both development and PyInstaller environments
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.base_path = sys._MEIPASS
            self.script_dir = self.base_path  # Add this for consistency
        else:
            # Running in development environment
            self.script_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_path = os.path.dirname(self.script_dir)
        
        print(f"Base path: {self.base_path}")
        print(f"Script directory: {self.script_dir}")
        
        # Define paths relative to base_path
        self.dependencies_bat = self.get_resource_path("config", "dependencies-1.bat")
        self.ipfs_config_bat = self.get_resource_path("config", "ipfs_config.bat")
        
        print(f"Dependencies path: {self.dependencies_bat}")
        print(f"IPFS config path: {self.ipfs_config_bat}")

    def get_resource_path(self, *relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = self.base_path
            
            # Join the base path with the relative path components
            full_path = os.path.join(base_path, *relative_path)
            
            # Verify the path exists
            if not os.path.exists(full_path):
                print(f"Warning: Path does not exist: {full_path}")
            
            return full_path
        except Exception as e:
            print(f"Error resolving path: {e}")
            return None
     
    def total_setup(self):
        try:
            print("Entered total setup.")
            print(f"Current working directory: {os.getcwd()}")
            # Run dependencies batch file
            print(f"Running {self.dependencies_bat}")
            subprocess.run(self.dependencies_bat, shell=True, check=True)
            
            # Generate swarm key
            gen_swarm_key.enter_community_id()
            
            # Run IPFS config batch file
            print(f"Running {self.ipfs_config_bat}")
            subprocess.Popen(self.ipfs_config_bat, shell=True)
            
            time.sleep(6)

        except Exception as e:
            print(f"Error during total_setup: {e}")

    def start_daemon(self):
        try:
            print("Starting daemon.")
            print(f"path: {self.script_dir}")
            # Generate swarm key
            gen_swarm_key.enter_community_id()
            
            # Run IPFS config batch file
            print(f"Running {self.ipfs_config_bat}")
            subprocess.Popen(self.ipfs_config_bat, shell=True)

            time.sleep(6)
        except Exception as e:
            print(f"Error during start_daemon: {e}")
    
    def start_commander(self):
        try:
            cli = IPFSCommands(self.client_socket)
            print("IPFS CLI Started. Type 'exit' to quit.")
            print("Example commands: add <file>, cat <hash>, swarm peers, id")
            cli.execute_command()
        except Exception as e:
            print(f"Error in start_commander: {e}")

    def choosing_set_up(self):
        print("Starting setup.")
        try:
            if self.setup_type == "total":
                self.total_setup()
                self.start_commander()
            elif self.setup_type == "daemon":
                self.start_daemon()
                self.start_commander()
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error in choosing_set_up: {e}")
