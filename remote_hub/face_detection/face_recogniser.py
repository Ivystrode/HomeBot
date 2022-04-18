import numpy as np
from cv2 import cv2 as cv 
import os, time


def recognise_face(image):
    haar_cascade = cv.CascadeClassifier('haar_face.xml')
    
    # need to make sure we actually have this folder in order to list people whose faces we are detecting
    # or use another means of assigning names to the indexes that the labels file holds (maybe just hardcoded list?)
    people = [person for person in os.listdir(r'training')]
    
    # Load features and labels arrays from saved file
    # Easier to use the people folder as these will just give an index/number
    # features = np.load('features.npy', allow_pickle=True)
    # labels = np.load('labels.npy')

    # Load the face recogniser
    face_recogniser = cv.face.LBPHFaceRecognizer_create()
    face_recogniser.read('face_trained.yml')

    img = cv.imread(image)

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    #Detect the face
    faces_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=9)
    
    face_detections = []
    face_images = []
        
    
    print(f"{len(faces_rect)} face/s detected")

    for (x,y,w,h) in faces_rect:
        faces_roi = gray[y:y+h,x:x+w]

        label, confidence = face_recogniser.predict(faces_roi)
        person = people[label]
        
        cv.putText(img, str(people[label]), (20,20), cv.FONT_HERSHEY_COMPLEX, 1.0, (0,255,0), 2)
        cv.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        
        det = {"name": person, "confidence": confidence}
        face_detections.append(det)
        
    return face_detections
        
    
if __name__ == '__main__':
    
    dets = recognise_face("test/char2.jpg")

    for n in dets:
        print(f"I think it's {n['name']}")
        print(f"with confidence of {n['confidence']}")
        if n['confidence'] < 50:
            print(f"so its probably not {n['name']}")
        else:
            print(f"so it could be {n['name']}")
        print("\n")
