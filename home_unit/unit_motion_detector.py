from main_unit import Unit
from signaller import Signaller
from cam import Camera
import threading, time

from gpiozero import MotionSensor

class MotionDetectorUnit(Unit):
    
    def __init__(self, unit_type, testing=False):
        super().__init__(unit_type, testing)
        
        self.motion_detection = threading.Thread(target=self.detect_motion)
        
        
        self.camera = Camera(signaller=Signaller(self.hub_addr, # could also just pass self so camera can use the unit's original signaller
                                                 self.send_port, 
                                                 self.file_send_port),
                             testing=self.testing)
        
    def detect_motion(self):
        pir = MotionSensor(17)
        pir.wait_for_motion()
        print('motion detected')
        self.signaller.message_to_hub("Motion detected", "sendtobot")
        pir.wait_for_no_motion()
        print('motion ceased')
        time.sleep(5)

    def start_object_detection(self):
        try:
            self.camera.object_detection_active = True
            self.camera.object_detection.start()
        except Exception as e:
            self.signaller.message_to_hub(f"Unable to start object detection: {e}", "sendtobot")
            self.camera.object_detection_active = False
            
    def stop_object_detection(self):
        self.camera.object_detection_active = False
        self.camera.stop_im_recog()
        
    def start_live_stream(self):
        self.camera.start_live_stream()
        
    def stop_live_stream(self):
        self.camera.stop_live_stream()
        
if __name__ == '__main__':
    motion_detector = MotionDetectorUnit("Motion detector")
