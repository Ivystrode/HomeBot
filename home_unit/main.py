import random, socket, threading 
from decouple import config

# import cam
from signaller import Signaller
from cam import Camera

class HomeUnit():
    """
    The main instance of the camera unit
    """
    
    def __init__(self):
        self.name = socket.gethostname()
        self.hub_addr = config("LOCAL_HUB_ADDRESS")
        self.id = random.randint(1, 1000000)
        
        self.receive_port = config("LOCAL_UNIT_RECV_PORT")
        self.send_port = config("LOCAL_HUB_RECV_PORT")
        self.file_send_port = config("LOCAL_HUB_FILE_RECV_PORT")
        
        self.camera = Camera(signaller=Signaller(self.hub_addr, 
                                                 self.send_port, 
                                                 self.file_send_port))
        self.signaller = Signaller(self.hub_addr, 
                                   self.send_port, 
                                   self.file_send_port)
        
        self.hub_listener = threading.Thread(target=self.listen_for_hub)
        
        
    def activate(self):
        self.hub_listener.start()       
        self.signaller.message_to_hub("Activated", self.id)
        
    def listen_for_hub(self):
        while True:
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0',self.receive_port))
            s.listen(5)
            try:
                hub_socket, hub_address = s.accept()
                raw_message = hub_socket.recv(self.BUFFER_SIZE).decode()
                cleaned_message = raw_message.split(self.SEPARATOR)

                hub_name = cleaned_message[0]
                message = cleaned_message[1]
                print(f"Message from {hub_name} at {hub_address}: {message}")
                
                s.close()
                
            except Exception as e:
                print(f"Receive from local network error: {e}")
        
    def start_object_detection(self):
        self.camera.im_recog()

if __name__ == '__main__':
    unit = HomeUnit()
    unit.start()