import hashlib, logging, os, random, socket, subprocess, threading, time
from decouple import config

from signaller import Signaller

logging.basicConfig(filename="main_unit.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Unit():
    """
    The parent class of units (an abstract base class)
    Units (atm) will either be camera, rfcontroller or motion detector
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
        
        self.signaller = Signaller(self.hub_addr, 
                                   self.send_port, 
                                   self.file_send_port)
        
        self.hub_listener = threading.Thread(target=self.listen_for_hub)
        self.temp_warning_timer = threading.Thread(target=self.warning_countdown)
        
        self.hub_listener.start()    
        self.temp_warning_timer.start() 
        self.signaller.message_to_hub("Activated", str(self.id), self.type)
        print("Activation message sent")
        
    def __str__(self) -> str:
        return f"{self.name}: {self.type}"
    
    # @abstractmethod
    def command_router(self, command, *args):
        cmd = getattr(self, command)
        try:
            if args:
                logger.info(f"Command {command} received - with args: {args}")
                cmd(str(args[0]))
                logger.info(f"Command {command} completed")
            else:
                logger.info(f"Command {command} received")
                cmd()
                logger.info(f"Command {command} completed")
        except Exception as e:
            logger.error(f"Error with {command}: {e}")
            self.signaller.message_to_hub(f"Error with {command}: {e}", "sendtobot")
            logger.info(f"Error message sent to hub")
        
    def get_id(self):
        hasher = hashlib.sha1()
        encoded_id = self.name.lower().encode()
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
                try:
                    detail = cleaned_message[2]
                except:
                    detail = None
                print(f"Message from {hub_name} at {hub_address}: {message}")

                if message == "reboot":
                    print("REBOOTING")
                    subprocess.run(['sudo','reboot','now'])
                else:
                    if detail is None:
                        self.command_router(message)
                    else:
                        self.command_router(message, detail)
                    
                s.close()
                
            except Exception as e:
                print(f"Receive from local network error: {e}")
                
    def warning_countdown(self):
        while True:
            time.sleep(1800)
            core_temp = os.popen("vcgencmd measure_temp").read()[5:9]
            core_temp = float(core_temp)
            if core_temp > 55.0:
                self.signaller.message_to_hub(f"Core temperature warning - {core_temp}", "sendtobot")
        
