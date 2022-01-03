from decouple import config
import socket 

def is_remote():
    """
    Check which machine we are running on and use that machine's params
    """
    # if remote return True
    # else return False

remote = is_remote()

if remote:
    PORT = config("REMOTE_SERVER_RECV_PORT")
else:
    PORT = config("LOCAL_SERVER_RECV_PORT")


# while True
s = socket.socket() 
s.bind(('0.0.0.0', PORT))
s.listen()

client, address = s.accept()
msg = client.recv(1024).decode()
print(msg)
