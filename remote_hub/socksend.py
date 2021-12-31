from decouple import config
import socket

"""
Both socksend and sockrecv live on the local and remote machine to allow them to send messages to each other...

Local sends on one port and receives on another. Remote uses the same ports but opposite send/receive.
"""

def is_remote():
    """
    Check which machine we are running on and use that machine's params
    """
    # if remote return True
    # else return False

remote = is_remote()

if remote:
    SERVER = config("LOCAL_SERVER_IP")
    PORT = config("LOCAL_SERVER_RECV_PORT")
else:
    SERVER = config("REMOTE_SERVER_IP")
    PORT = config("REMOTE_SERVER_RECV_PORT")
    

s = socket.socket()
s.connect((SERVER, PORT))
print("connected")
m = "hi"
s.send(m.encode())