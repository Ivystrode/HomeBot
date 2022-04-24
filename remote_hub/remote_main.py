from decouple import config
import socket, threading
import ntpath

import bot 

class RemoteHub():
    
    def __init__(self) -> None:
        # setup
        self.BUFFER_SIZE = 1024
        self.SEPARATOR = "<SEPARATOR>"
        
        self.send_port = int(config("LOCAL_SERVER_RECV_PORT"))
        self.recv_port = int(config("REMOTE_SERVER_RECV_PORT"))
        
        # thread not needed until we're multitasking
        # self.local_server_listener_thread = threading.Thread(target=self.local_server_listener, daemon=True)
        # self.local_server_listener_thread.start()
        
        print("[REMOTE HUB] Activated")
        self.local_server_listener()
        
        
    def local_server_listener(self):
        # while True:
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.recv_port))
        s.listen()
        try:
            local_socket, local_address = s.accept()
            raw_message = local_socket.recv(self.BUFFER_SIZE).decode()
            cleaned_message = raw_message.split(self.SEPARATOR)

            message = cleaned_message[0]
            print(f"Message from {local_address}: {message}")
            
            if message == "file_incoming":
                msg, file, filesize, file_description, file_type = raw_message.split(self.SEPARATOR)
                filesize = int(filesize)
                filename = ntpath.basename(file)
                
                with open(filename, "wb") as f:
                    for _ in range(filesize):
                        bytes_read = local_socket.recv(self.BUFFER_SIZE)
                        
                        if not bytes_read:
                            break
                        
                        f.write(bytes_read)
                        
                print("file received")

            s.close()
            
        except Exception as e:
            print(f"Receive from local error: {e}")
            
        self.local_server_listener()
                
if __name__ == '__main__':
    remote_hub = RemoteHub()