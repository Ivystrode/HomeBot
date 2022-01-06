import random, socket, threading 
from decouple import config

# import cam
from signaller import Signaller
from cam import Camera

class HomeUnit():
    """
    The main instance of the camera unit
    """
    
    def __init__(self, unit_type, testing=False):
        self.name = socket.gethostname()
        if not testing:
            self.hub_addr = config("LOCAL_HUB_ADDRESS")
        else:
            self.hub_addr = socket.gethostbyname(socket.gethostname())
        self.id = random.randint(1, 1000000)
        self.type = unit_type
        self.testing = testing
        
        self.receive_port = int(config("LOCAL_UNIT_RECV_PORT"))
        self.send_port = int(config("LOCAL_HUB_RECV_PORT"))
        self.file_send_port = int(config("LOCAL_HUB_FILE_RECV_PORT"))
        self.BUFFER_SIZE = 1024
        self.SEPARATOR = "<SEPARATOR>"
        
        self.camera = Camera(signaller=Signaller(self.hub_addr, 
                                                 self.send_port, 
                                                 self.file_send_port),
                             testing=self.testing)
        
        self.signaller = Signaller(self.hub_addr, 
                                   self.send_port, 
                                   self.file_send_port)
        
        self.hub_listener = threading.Thread(target=self.listen_for_hub)
        
        
    def activate(self):
        self.hub_listener.start()       
        print("Activating...")
        self.signaller.message_to_hub("Activated", str(self.id), self.type)
        print("Activation message sent")
        
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

                if message == "start_object_detection":
                    self.start_object_detection()
                if message == "send_photo":
                    if not self.camera.object_detection_active:
                        self.camera.capt_img()
                    else:
                        self.signaller.message_to_hub("Unable to take photo - object detection is using camera resource", "sendtobot")
                    
                s.close()
                
            except Exception as e:
                print(f"Receive from local network error: {e}")
        
    def start_object_detection(self):
        self.camera.object_detection_active = True
        self.camera.object_detection.start()
            
        
    def stop_object_detection(self):
        self.camera.object_detection_active = False
        
    def start_live_stream(self):
        self.camera.start_live_stream()
        
    def stop_live_stream(self):
        self.camera.stop_live_stream()

if __name__ == '__main__':
    unit = HomeUnit("camera")
    unit.activate()