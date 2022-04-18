import os
from cv2 import cv2 as cv
import numpy as np

people = []

for i in os.listdir(r'training'):
    people.append(i)

DIR = 'training'

features = []
labels = []

haar_cascade = cv.CascadeClassifier('haar_face.xml')

def create_train():
    print(people)
    for person in people:
        path = os.path.join(DIR, person)
        label = people.index(person)
        
        for img in os.listdir(path):
            img_path = os.path.join(path, img)
            print(img_path)
            
            img_array = cv.imread(img_path)
            gray = cv.cvtColor(img_array, cv.COLOR_BGR2GRAY)
            
            faces_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=7)

            for (x,y,w,h) in faces_rect:
                faces_roi = gray[y:y+h, x:x+w] # the face region of interest
                features.append(faces_roi) # put the roi coords in the list
                labels.append(label) # using the numerical index as a label reduces the strain on computer by creating a mapping between string and num label

create_train()

# This will tell us how many faces it has detected - will both be the same number
print("Features")
print(len(features))
print("labels")
print(len(labels))

# We then use this to train a model
features = np.array(features, dtype='object')
labels = np.array(labels)

face_recogniser = cv.face.LBPHFaceRecognizer_create()

# Train the recogniseron the features list and labels list
# It then matches the features to the labels given since the indexes on each list match

face_recogniser.train(features, labels)

# Save the model to be used in other files etc
face_recogniser.save('face_trained.yml')
np.save('features.npy', features)
np.save('labels.npy', labels)


            