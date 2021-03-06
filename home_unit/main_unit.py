import hashlib, os, random, socket, subprocess, threading, time
from decouple import config

from signaller import Signaller

class Unit():
    """
    The parent class of units
    Units (atm) will either be camera or rfcontroller
    """
    
    def __init__(self, unit_type, testing=False):
        self.name = socket.gethostname()
        self.id = self.get_id()
        self.type = unit_type
        self.testing = testing
        
        if not testing:
            self.hub_addr = config("LOCAL_HUB_ADDRESS")
        else:
            self.hub_addr = socket.gethostbyname(socket.gethostname())
            
        self.receive_port = int(config("LOCAL_UNIT_RECV_PORT"))
        self.send_port = int(config("LOCAL_HUB_RECV_PORT"))
        self.file_send_port = int(config("LOCAL_HUB_FILE_RECV_PORT"))
        self.BUFFER_SIZE = 1024
        self.SEPARATOR = "<SEPARATOR>"
            
        
        # stops it sending core temp warnings constantly
        self.temp_warning_timer = threading.Thread(target=self.warning_countdown)
        self.temp_warnings_enabled = True
        
        
        self.signaller = Signaller(self.hub_addr, 
                                   self.send_port, 
                                   self.file_send_port)
        
        self.hub_listener = threading.Thread(target=self.listen_for_hub)
        
        
        self.hub_listener.start()     
        self.signaller.message_to_hub("Activated", str(self.id), self.type)
        print("Activation message sent")
        
    def __str__(self) -> str:
        return self.type
        
    def get_id(self):
        hasher = hashlib.sha1()
        encoded_id = socket.gethostname().lower().encode()
        hasher.update(encoded_id)
        return str(hasher.hexdigest())
        
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
                if message == "stop_object_detection":
                    self.stop_object_detection()
                if message == "send_photo":
                    if not self.camera.object_detection_active:
                        print("Taking picture")
                        self.camera.capt_img()
                    else:
                        print("Object detection active, can't take picture")
                        self.signaller.message_to_hub("Unable to take photo - object detection is using camera resource", "sendtobot")
                if message == "reboot":
                    print("REBOOTING")
                    subprocess.run(['sudo','reboot','now'])

                # USING THE STRING AS THE FUNCTION NAME TO CALL:
                # command = getattr(self, message)
                # try:
                #     command()
                # except Exception as e:
                #     print("MAIN: Message not recognised as command (error: {e}).")
                    
                s.close()
                
                # check temperature
                core_temp = os.popen("vcgencmd measure_temp").read()[5:9]
                core_temp = float(core_temp)
                if core_temp > 55.0 and self.temp_warnings_enabled:
                    self.signaller.message_to_hub(f"Core temperature warning - {core_temp}", "sendtobot")
                    self.temp_warnings_enabled = False
                
            except Exception as e:
                print(f"Receive from local network error: {e}")
                
    def warning_countdown(self):
        while True:
            time.sleep(1800)
            self.temp_warnings_enabled = True
        
