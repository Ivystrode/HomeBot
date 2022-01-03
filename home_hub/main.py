from decouple import config
from tqdm import tqdm

import ntpath, socket, threading
import bot, bot_db

class HomeHub():
    """
    The instance of the home hub
    Runs the bot, wifi scanner, and other things
    """
    def __init__(self) -> None:
        
        # setup
        self.BUFFER_SIZE = 1024
        self.SEPARATOR = "<SEPARATOR>"
        
        # Remote server
        self.remote_recv_port = config("LOCAL_SERVER_RECEIVE_PORT") # listen on this
        self.remote_send_port = config("REMOTE_SERVER_RECEIVE_PORT") # send on this
        
        # Local network comms
        self.local_recv_port = config("LOCAL_HUB_RECEIVE_PORT") # listen on this
        self.unit_send_port = config("LOCAL_UNIT_RECEIVE_PORT") # send on this
        self.file_recv_port = config("LOCAL_HUB_FILE_RECV_PORT") # listen on this
        
        self.unit_listener = threading.Thread(target=self.listen_for_units)
        self.remote_server_listener = threading.Thread(target=self.remote_server_listener)
        self.file_listener = threading.Thread(target=self.file_receiver)
        

        
    def activate_hub(self):
        bot.activate_bot()
        self.activate_hub()
        self.unit_listener.start()
        self.remote_server_listener.start()
        
    def listen_for_units(self):
        while True:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0',self.local_recv_port))
            s.listen(5)
            try:
                unit_socket, unit_address = s.accept()
                raw_message = unit_socket.recv(self.BUFFER_SIZE).decode()
                cleaned_message = raw_message.split(self.SEPARATOR)

                unit_name = cleaned_message[0]
                message = cleaned_message[1]
                print(f"Message from {unit_name}: {message}")
                
                s.close()
                
            except Exception as e:
                print(f"Receive from local network error: {e}")
            
    def remote_server_listener(self):
        while True:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.remote_recv_port))
            s.listen(5)
            try:
                remote_socket, remote_address = s.accept()
                raw_message = remote_socket.recv(self.BUFFER_SIZE).decode()
                cleaned_message = raw_message.split(self.SEPARATOR)

                remote_name = cleaned_message[0]
                message = cleaned_message[1]
                print(f"Message from {remote_name} at {remote_address}: {message}")

                s.close()
                
            except Exception as e:
                print(f"Receive from remote error: {e}")
                
        
    def file_listener(self):
        while True:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0',self.file_recv_port))
            s.listen(5)
            try:
                file_socket, unit_address = s.accept() # did i close this??
                unit_name = bot_db.get_unit_name(unit_address[0])
                print(f"[HUB] Incoming file from {unit_name}")
                
                try:
                    received = file_socket.recv(self.BUFFER_SIZE).decode()
                except:
                    received = file_socket.recv(self.BUFFER_SIZE).decode("iso-8859-1")
                    
                if unit_name is not None:
                    
                    print(f"[HUB] Receiving file from {unit_name}")
                    file, filesize, file_description, file_type = received.split(self.SEPARATOR)
                    filesize = int(filesize)
                    filename = ntpath.basename(file)
                    
                    progress = tqdm(range(filesize), f"[HUB] Progress {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                    with open(filename, "wb") as f: 
                        for _ in progress:
                            bytes_read = file_socket.recv(self.BUFFER_SIZE)
                            if not bytes_read:

                                break
                            f.write(bytes_read)
                            progress.update(len(bytes_read))
                            
                    # send to bot to send to users
                    try:
                        bot.send_message(f"{file_type} incoming from {unit_name}...")
                        bot.send_file(unit_name, filename, file_description)
                    except Exception as e:
                        bot.send_message(f"File send attempt failed: {e}")
                    
                    s.close()
                
                
            except Exception as e:
                print(f"Receive from local network error: {e}")
                
if __name__ == '__main__':
    hub = HomeHub()
    hub.activate_hub()