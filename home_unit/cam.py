import shutil
import socket
import cv2
import time
import threading
import os
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
        self.detection_thread = threading.Thread(target=self.im_recog)
    
        self.name = socket.gethostname()
        self.object_detection_active = False
        self.detection_duration = 30

        self.font_scale = 2
        self.font = cv2.FONT_HERSHEY_PLAIN

        self.self.SEPARATOR = "<self.SEPARATOR>"
        self.BUFFER_SIZE = 1024

    # ==========Log all actions==========
    def log(self, action):
        with open("log.txt", "a") as f:
            f.write(action)
            

    # ==========Basic image capture & send to hub==========

    # Take a picture
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
        
    # ==========Send photo to hub==========
    def send_photo(self, hub_addr, port, file, file_description):
        s = socket.socket()
        print(f"Connecting to hub...")
        s.connect((hub_addr, port))
        filesize = os.path.getsize(file)
        file_type = "photo"

        print(f"Sending file: {file}")
        s.send(f"{file}{self.SEPARATOR}{filesize}{self.SEPARATOR}{file_description}{self.SEPARATOR}{file_type}".encode())
        try:
            progress = tqdm(range(filesize), f"Sending {file}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(file, "rb") as f:
                for _ in progress:
                    try:
                        bytes_read = f.read(self.BUFFER_SIZE)
                        
                        if not bytes_read:
                            break
                        
                        s.sendall(bytes_read)
                        progress.update(len(bytes_read))
                    except Exception as e:
                        print(f"FILE SEND ERROR: {e}")
                        break
        except Exception as e:
            print(f"FILE SEND ERROR - outside - {e}")
        print(f"{file} sent to hub")
        s.close()



    # ==========Object recognition==========
    def im_recog(self, counts_before_detect_again=60):
        """
        Runs image detection model on the pi, saves pictures of people
        """
        time.sleep(0.5)
        
        # this stops the pi saving too many images, we just force it to pause object detection
        detection = False
        # counts_before_detect_again = 0
            
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
        self.object_detection_active = True
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
                                        self.signaller.message(1, 1, imgfile, f"{self.name} detected person at {datetime.now().strftime('%H%M%S')}")
                                    
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
        camera.close()
        cv2.destroyAllWindows()
        
        

    

