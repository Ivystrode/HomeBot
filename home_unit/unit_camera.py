import logging
from main_unit import Unit
from cam import Camera
from signaller import Signaller

class CameraUnit(Unit):
    
    def __init__(self, unit_type, testing=False):
        super().__init__(unit_type, testing)
        
        
        self.camera = Camera(signaller=Signaller(self.hub_addr, # could also just pass self so camera can use the unit's original signaller
                                                 self.send_port, 
                                                 self.file_send_port),
                             testing=self.testing)

    def send_photo(self):
        if not self.camera.object_detection_active:
            self.camera.capt_img()
        else:
            self.signaller.message_to_hub("Unable to take photo - object detection is using camera resource", "sendtobot")
            
    def start_object_detection(self):
        logger.info("Object detection told to start")
        try:
            logger.info("Setting obj det active to true")
            self.camera.object_detection_active = True
            logger.info("Start obj det thread")
            self.camera.object_detection.start()
            logger.info("Object detection thread started")
        except Exception as e:
            logger.error(f"Object detection failed to start - {e}")
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
    camera = CameraUnit("camera")
    logging.basicConfig(filename="cam_unit.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)