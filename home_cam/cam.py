import shutil
import socket
import cv2
import time
import threading
import subprocess
import numpy as np
from datetime import datetime

from picamera import PiCamera
from picamera.array import PiRGBArray
from datetime import datetime
import wifi

from tqdm import tqdm

label = "[" + socket.gethostname().upper() + "]"
name = socket.gethostname()
file_channel = 7503 # same as status channel which hub is listening on. make a third channel if necessary/possible (i think it was necessary)

object_detection_active = False
detection_duration = 30

font_scale = 2
font = cv2.FONT_HERSHEY_PLAIN

# ==========Log all actions==========
def log(action):
    with open("log.txt", "a") as f:
        f.write(action)
        

# ==========Basic image capture & send to hub==========

# Take a picture
def capt_img(hub_addr):
    """
    Basic picture taking with pi camera
    """
    print(f"{label} Capture image")
    img_name = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(name) + ".jpg"
    camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.vflip = True
    camera.hflip = True
    camera.start_preview()
    time.sleep(0.5) # apparently camera has to "warm up"
    camera.capture(img_name)
    time.sleep(0.5)
    camera.close()
    print(f"{label} Image saved as {img_name}")



# ==========Object recognition==========
def im_recog():
    """
    Runs image detection model on the pi, saves pictures of people or motorbikes
    If it detects a motorbike it takes a picture AND activates the wifi scanner
    """
    global object_detection_active
    time.sleep(0.5)
    
    # this stops the pi saving too many images, we just force it to pause object detection
    detection = False
    counts_before_detect_again = 0
        
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
    object_detection_active = True
    while True:
        if object_detection_active:
            for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
                
                image = frame.array

                ClassIndex, confidence, bbox = model.detect(image, confThreshold=0.55)

                if len(ClassIndex) != 0:
                    for ClassInd, conf, boxes in zip(ClassIndex.flatten(), confidence.flatten(), bbox):
                        if ClassInd <= 80:
                            if labels[ClassInd-1] == "person":
                                # these aren't working in this implementation
                                cv2.rectangle(image, boxes, (0,255,0), 2)
                                cv2.putText(image, f"{labels[ClassInd-1].capitalize()}: {round(float(conf*100), 1)}%",(boxes[0], boxes[1]-10), font, fontScale=font_scale, color=(0,255,0), thickness=2)

                                if not detection:
                                    imgfile = f'{labels[ClassInd-1].capitalize()}_detection_{datetime.now().strftime("%H%M%S")}.jpg'
                                    cv2.imwrite(f'{labels[ClassInd-1].capitalize()} detection_{datetime.now().strftime("%H%M%S")}.jpg', image)
                                    log(f"{datetime.now().strftime('%H%M')} - {labels[ClassInd-1]}_detected")
                                    detection = True
                                    print(f"{labels[ClassInd-1]} detected, dimensions: {boxes}, confidence: {round(float(conf*100), 1)}%")
                                    #wifi_thread.start()
                                    wifi.activate_monitor_mode("10")
                                
                            if labels[ClassInd-1] == "motorbike":
                                # these aren't working in this implementation
                                cv2.rectangle(image, boxes, (0,255,0), 2)
                                cv2.putText(image, f"{labels[ClassInd-1].capitalize()}: {round(float(conf*100), 1)}%",(boxes[0], boxes[1]-10), font, fontScale=font_scale, color=(0,255,0), thickness=2)

                                if not detection:
                                    imgfile = f'{labels[ClassInd-1].capitalize()} detection_{datetime.now().strftime("%H%M%S")}.jpg'
                                    cv2.imwrite(f'{imgfile}', image)
                                    log(f"{datetime.now().strftime('%H%M')} - {labels[ClassInd-1]}_detected")
                                    detection = True
                                    print(f"{labels[ClassInd-1]} detected, dimensions: {boxes}, confidence: {round(float(conf*100), 1)}%")
                                    print("activate wifi scanner...")
                                    # wifi.activate_monitor_mode("20")
                                    wifi_thread.start()
                                
                if detection:
                    # this is basically a timer that stops the pi saving millions of images
                    counts_before_detect_again += 1
                    if counts_before_detect_again > 60: 
                        detection = False
                        counts_before_detect_again = 0
                        
                    # monitor present only
                    # cv2.imshow("Video detection", frame)

                # only relevant if testing unit with a monitor/keyboard connected...
                if cv2.waitKey(5) & 0xFF == ord("c"):
                    object_detection_active = False
                    break
                
                raw_capture.truncate(0)
                
        else:
            break
        
    print("end of detection")
    camera.close()
    cv2.destroyAllWindows()
    
    

detection_thread = threading.Thread(target=im_recog)
wifi_thread = threading.Thread(target=wifi.activate_monitor_mode, daemon=True, args=("9"))


detection_thread.start()