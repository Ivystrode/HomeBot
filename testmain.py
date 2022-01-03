from testcam import Camera
from testsignaller import Signaller

class Main():
    
    def __init__(self, camera) -> None:
        self.camera = camera
    
    def activate(self):
        self.camera.test()
        
if __name__ == '__main__':
    m = Main(camera=Camera(signaller=Signaller(hub_addr="hubaddrtest", port=12, file_port=17)))
    m.activate()