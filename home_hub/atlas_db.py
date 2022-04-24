"""
This file handles sending data from the homebot system to the Mongo Atlas DB
"""
import json, requests, random

posturl = "http://localhost:5000/post"

def add_camera(id, name, address, type, status):
    camera_details = {
        "id": id,
        "name": name,
        "address": address,
        "type": type,
        "status": status
    }
    p = requests.post(f"{posturl}/cameras", json=camera_details)
    print(p)
    
def add_detection(detection_unit, detection_type, time, image):
    detection_details = {
        "id": random.randint(1, 10000000),
        "type": detection_type,
        "detection_unit": detection_unit,
        "time": time,
        "image": image
    }
    p = requests.post(f"{posturl}/detections", json=detection_details)
    print(p)
    return p