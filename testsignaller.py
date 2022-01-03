class Signaller():
    def __init__(self, hub_addr, port, file_port):
        self.hub_addr = hub_addr
        self.port = port 
        self.file_port = file_port
        self.SEPARATOR = "<SEPARATOR>"
    
    def message(self, msg):
        print(msg)
        print(self.hub_addr)