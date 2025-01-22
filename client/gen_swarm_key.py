import hashlib 
import secrets 

import subprocess

def enter_community_id():
    password=input("Enter Community ID: ")
    key = hashlib.sha256(password.encode()).hexdigest()
    path=r"%USERPROFILE%\.ipfs\swarm.key"
    with open("swarm.key", "w") as f: 
        f.write(f"/key/swarm/psk/1.0.0/\n/base16/\n{key}") 
    command=f"move swarm.key {path}"
    subprocess.run(command, shell=True, check=True)



