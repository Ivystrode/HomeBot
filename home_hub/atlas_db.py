"""
This file handles sending data from the homebot system to the Mongo Atlas DB
"""
import json, requests

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