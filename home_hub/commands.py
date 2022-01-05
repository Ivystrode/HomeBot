import socket 
import bot_db

def send_command(self, unit, command):
    unit_addr = bot_db.get_unit_address(unit)
    s = socket.socket() 
    s.connect((unit_addr, self.unit_send_port))
    message = f"{socket.gethostname()}{self.SEPARATOR}{command}"
    s.send(message.encode())
    print(f"Message sent to {unit}")
    s.close()