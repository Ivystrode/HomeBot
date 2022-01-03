from testcam import Camera
from testsignaller import Signaller

class Main():
    
    def __init__(self, camera) -> None:
        self.camera = camera
    
    def activate(self):
        self.camera.test()
        
if __name__ == '__main__':
    m = Main(camera=Camera(signaller=Signaller))
    m.activate()