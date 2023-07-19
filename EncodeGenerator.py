# Generate data for all those 128 measurements and then store it in a file
# We will import this file to recognise faces
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# # for connecting with firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognitionattendanc-b5522-default-rtdb.firebaseio.com/",
    'storageBucket':"facerecognitionattendanc-b5522.appspot.com"
})


# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []

# storing the image encoding in a list
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    #print(path)
    #print(os.path.splitext(path)[0])
#print(len(imgList))
    studentIds.append(os.path.splitext(path)[0])

    # to send images to firebase storage
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
print(studentIds)


# function to generate the encodings and return list with encodings
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
#print(encodeListKnown)
print("Encoding Complete")

# saving the encodings in a pickle file,
# we can import it when we use the webcam
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")