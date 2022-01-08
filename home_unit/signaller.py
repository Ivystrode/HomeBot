import os, random, socket
from decouple import config
from tqdm import tqdm

class Signaller():
    """
    Sends and receives commands from the hub
    (include backup function to send to remote hub if no response from home hub)
    """
    
    def __init__(self, hub_addr, port, file_port):
        self.hub_addr = hub_addr
        self.port = port
        self.file_port = file_port
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 1024
        print(f"Signaller:\nHub: {self.hub_addr}\nPort:{str(self.port)}")
        
    def message_to_hub(self, message, *args):
        """
        Send messages to hub
        Pattern: unitname-message-args
        In activation message the first arg is always the unit ID
        Unit name is included by Signaller automatically
        """
        s = socket.socket() 
        s.connect((self.hub_addr, self.port))
        message = f"{socket.gethostname()}{self.SEPARATOR}{message}"
        for item in args:
            message += f"{self.SEPARATOR}{item}"
        s.send(message.encode())
        print("Message sent to hub")
        s.close()
        
    def send_file(self, file, file_description, file_type="photo"):
        s = socket.socket()
        print(f"Connecting to hub...")
        s.connect((self.hub_addr, self.file_port))
        filesize = os.path.getsize(file)

        print(f"Sending file: {file}")
        s.send(f"{file}{self.SEPARATOR}{filesize}{self.SEPARATOR}{file_description}{self.SEPARATOR}{file_type}".encode())
        
        f = open(file, "rb")
        while True:
            l = f.read(self.BUFFER_SIZE)
            while l:
                s.send(l) 
                l = f.read(self.BUFFER_SIZE)
            if not l:
                f.close()
                s.close()
                break
        print("Sent====================")
        
        # try:
        #     progress = tqdm(range(filesize), f"Sending {file}", unit="B", unit_scale=True, unit_divisor=1024)
        #     with open(file, "rb") as f:
        #         for _ in progress:
        #             try:
        #                 bytes_read = f.read(self.BUFFER_SIZE)
                        
        #                 if not bytes_read:
        #                     break
                        
        #                 s.sendall(bytes_read)
        #                 progress.update(len(bytes_read))
        #             except Exception as e:
        #                 print(f"FILE SEND ERROR: {e}")
        #                 break
        # except Exception as e:
        #     print(f"FILE SEND ERROR - outside - {e}")
        # print(f"{file} sent to hub")
        # s.close()