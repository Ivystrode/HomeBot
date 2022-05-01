import socket 
import bot_db
from decouple import config

def send_command(unit, command, *args):
    SEPARATOR = "<SEPARATOR>"
    send_port = int(config("LOCAL_UNIT_RECV_PORT"))
    unit_addr = bot_db.get_unit_address(unit)
    s = socket.socket() 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((unit_addr, send_port))
    
    if not args:
        message = f"{socket.gethostname()}{SEPARATOR}{command}"
    else:
        message = f"{socket.gethostname()}{SEPARATOR}{command}{SEPARATOR}{args[0]}"
        
    s.send(message.encode())
    print(f"Message sent to {unit}")
    s.close()