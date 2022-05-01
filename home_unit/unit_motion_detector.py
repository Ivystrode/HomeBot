from main_unit import Unit
from signaller import Signaller
from cam import Camera
import threading, time

from gpiozero import MotionSensor

class MotionDetectorUnit(Unit):
    
    def __init__(self, unit_type, motion_sensing=True, testing=False, sensor_pin=17, has_camera=True):
        super().__init__(unit_type, testing)
        
        self.pir_sensor = MotionSensor(sensor_pin)
        self.motion_sensing = motion_sensing
        self.motion_detection = threading.Thread(target=self.detect_motion, daemon=True)
        self.motion_detection.start()
        
        self.has_camera = has_camera
        
        if self.has_camera:
            self.camera = Camera(signaller=Signaller(self.hub_addr, # could also just pass self so camera can use the unit's original signaller
                                                    self.send_port, 
                                                    self.file_send_port),
                                testing=self.testing)
        
    def camerafunction(func):
        """
        Only call the requested function if the motion
        detector unit has a camera assigned (not necessarily
        available)
        """
        def inner(self):
            if not self.has_camera:
                print("No camera assigned to this unit")
                self.signaller.message_to_hub("No camera available", "sendtobot")
                return
            else:
                print("Calling camera function")
                func(self)
        return inner

    def detect_motion(self):
        while self.motion_sensing:
            self.pir_sensor.wait_for_motion()
            self.signaller.message_to_hub("Motion detection active", "sendtobot")
            print('motion detected')
            self.signaller.message_to_hub("Motion detected", "sendtobot")
            self.pir_sensor.wait_for_no_motion()
            print('motion ceased')
            time.sleep(5)

    @camerafunction
    def start_object_detection(self):
        try:
            self.camera.object_detection_active = True
            self.camera.object_detection.start()
        except Exception as e:
            self.signaller.message_to_hub(f"Unable to start object detection: {e}", "sendtobot")
            self.camera.object_detection_active = False
            
    @camerafunction    
    def stop_object_detection(self):
        self.camera.object_detection_active = False
        self.camera.stop_im_recog()
        
    @camerafunction 
    def start_live_stream(self):
        self.camera.start_live_stream()
        
    @camerafunction
    def stop_live_stream(self):
        self.camera.stop_live_stream()
        
if __name__ == '__main__':
    motion_detector = MotionDetectorUnit("Motion detector")
