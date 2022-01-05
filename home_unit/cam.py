import cv2, os, socket, subprocess, time, threading
import numpy as np
from datetime import datetime

from picamera import PiCamera
from picamera.array import PiRGBArray
from datetime import datetime
from tqdm import tqdm

class Camera():
    """
    Takes pictures, videos and runs object detections
    Uses Signaller to send to hub
    """
    
    def __init__(self, signaller) -> None:
        self.signaller = signaller
        self.object_detection = threading.Thread(target=self.im_recog) # no need to thread - its the only thing the camera will be doing anyway
        # YES actually so we can turn it off with a boolean
    
        self.name = socket.gethostname()
        self.object_detection_active = False
        self.detection_duration = 30

        self.font_scale = 2
        self.font = cv2.FONT_HERSHEY_PLAIN

        self.SEPARATOR = "<self.SEPARATOR>"
        self.BUFFER_SIZE = 1024
        
        print("Camera initialised")

    # ==========Log all actions==========
    def log(self, action):
        with open("log.txt", "a") as f:
            f.write(action)
            

    # ==========Basic image capture & send to hub==========
    def capt_img(self):
        """
        Basic picture taking with pi camera
        """
        print(f"Capture image")
        img_name = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(self.name) + ".jpg"
        camera = PiCamera()
        camera.resolution = (1024, 768)
        camera.vflip = True
        camera.hflip = True
        camera.start_preview()
        time.sleep(0.5) # apparently camera has to "warm up"
        camera.capture(img_name)
        time.sleep(0.5)
        camera.close()
        print(f"Image saved as {img_name}")
        self.signaller.send_file(img_name, f"Camera shot from {self.name}")
        
    # ==========Video stream==========
    # uses uv4f_raspicam now instead of motion - better framerate, larger image
    def start_motion(self):
        subprocess.run(['sudo','service','uv4l_raspicam','start']) 
        self.signaller.message_to_hub("Starting live video")
    
    def stop_motion(self):
        subprocess.run(['sudo','service','uv4f_raspicam','stop'])
        self.signaller.message_to_hub("Stopping live video")
        
    # ==========Object recognition==========
    def im_recog(self, counts_before_detect_again=60):
        """
        Runs image detection model on the pi, saves pictures of people
        """
        time.sleep(0.5)
        
        # when set to False this stops object detection
         # edit - this is controlled from the main.py file, see if this works...
        # self.object_detection_active = True
        
        # this stops the pi saving too many images, we just force it to pause object detection
        detection = False
        
            
        config_file = "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        frozen_model="frozen_inference_graph.pb"
        labels = []
        with open("Labels", "r") as f:
            labels = [line.strip() for line in f.readlines()]

        model = cv2.dnn_DetectionModel(frozen_model, config_file)
        model.setInputSize(320,320)
        model.setInputScale(1.0/127.5)
        model.setInputMean((127.5,127.5,127.5))
        model.setInputSwapRB(True)
        
        camera = PiCamera()
        camera.resolution = (1024, 768)
        camera.vflip = True
        camera.hflip = True
        camera.framerate = 32
        raw_capture = PiRGBArray(camera, size=(1024, 768))
        time.sleep(1)
            
        print("detecting active")
        while True:
            if self.object_detection_active:
                for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                    
                    image = frame.array

                    ClassIndex, confidence, bbox = model.detect(image, confThreshold=0.55)

                    if len(ClassIndex) != 0:
                        for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidence.flatten(), bbox):
                            if ClassInd <= 80:
                                if labels[ClassInd-1] == "person":
                                    # these aren't working in this implementation
                                    cv2.rectangle(image, boxes, (0,255,0), 2)
                                    cv2.putText(image, f"{labels[ClassInd-1].capitalize()}: {round(float(conf*100), 1)}%",(boxes[0], boxes[1]-10), self.font, fontScale=self.font_scale, color=(0,255,0), thickness=2)

                                    if not detection:
                                        imgfile = f'{labels[ClassInd-1].capitalize()}_detection_{datetime.now().strftime("%H%M%S")}.jpg'
                                        cv2.imwrite(f'{labels[ClassInd-1].capitalize()} detection_{datetime.now().strftime("%H%M%S")}.jpg', image)
                                        self.log(f"{datetime.now().strftime('%H%M')} - {labels[ClassInd-1]}_detected")
                                        detection = True
                                        print(f"{labels[ClassInd-1]} detected, dimensions: {boxes}, confidence: {round(float(conf*100), 1)}%")
                                        self.signaller.send_file(imgfile, f"{self.name}: detected person at {datetime.now().strftime('%H%M%S')}")
                                    
                    if detection:
                        # this is basically a timer that stops the pi saving millions of images
                        counts_before_detect_again += 1
                        if counts_before_detect_again > 60: 
                            detection = False
                            counts_before_detect_again = 0
                    # only relevant if testing unit with a monitor/keyboard connected...
                    if cv2.waitKey(5) & 0xFF == ord("c"):
                        self.object_detection_active = False
                        break
                    
                    raw_capture.truncate(0)
                    
            else:
                break
            
        print("end of detection")
        self.signaller.message_to_hub("Object detection deactivated")
        camera.close()
        cv2.destroyAllWindows()
        
        

    

