# importing required libraries
import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# for connecting with firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognitionattendanc-b5522-default-rtdb.firebaseio.com/",
    'storageBucket':"facerecognitionattendanc-b5522.appspot.com"
})

# retrieving bucket from Firebase Cloud Storage
bucket = storage.bucket()

# to start the webcam, 0 for internal, 1 for external
cap = cv2.VideoCapture(0)

# setting the cam image size according to the size of our background
cap.set(3, 640)
cap.set(4, 480)

# loading the background image
imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images into a list
# the path is folderModePath + path
# modeType
# 0 active
# 1 data
# 2 marked
# 3 already marked
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
#print(len(imgModeList))
#print(modePathList)


# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")


modeType = 0
counter = 0
id = -1
imgStudent = []

while True:

    # used to capture frames from a video stream or a video file
    success, img = cap.read()

    # resize image using scaling factors
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # detecting the face locations
    faceCurFrame = face_recognition.face_locations(imgS)
    # computing face encodings
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # setting webcam image position on the background image
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # setting the background mode at position
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    # if face is detected in current frame
    if faceCurFrame:
        # comparing encodings with generated encodings to match
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                # print("matches", matches)
                # print("faceDis", faceDis)

                matchIndex = np.argmin(faceDis)
                # print("Match Index", matchIndex)

                # If at the matched index we get correct face is detected
                if matches[matchIndex]:
                    print("Known Face Detected")
                    print(studentIds[matchIndex])

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1

                    # to add a rectangle around the face
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                    id = studentIds[matchIndex]

                    # for comparing only with the first frame
                    if counter == 0:
                        # Delay due to downloading of data from the database
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        cv2.imshow("Face Attendance", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 1    # data

                if counter != 0:
                    if counter == 1:
                        # Get the Data
                        studentInfo = db.reference(f'Students/{id}').get()
                        print(studentInfo)

                        # Get the Image from the storage
                        blob = bucket.get_blob(f'Images/{id}.png')
                        array = np.frombuffer(blob.download_as_string(), np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                        # Update data of attendance
                        datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                           "%Y-%m-%d %H:%M:%S")
                        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                        print(secondsElapsed)
                        if secondsElapsed > 30:
                            # sending student attendance on the database
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            # updating the last attendance time
                            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            # already marked mode
                            modeType = 3
                            counter = 0
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


                    # attendance is not marked
                    if modeType != 3:
                   
                        if 10 < counter < 20:
                            # marked mode
                            modeType = 2

                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                        if counter <= 10:
                            # putting the data at right locations on the image background
                            # scale, color, thickness
                            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(id), (1006, 493),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                            cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                            cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                            offset = (414 - w) // 2
                            cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                            # displaying this data on the background
                            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                        counter += 1
                        if counter >= 20:
                            counter = 0
                            # active mode
                            modeType = 0
                            studentInfo = []
                            imgStudent = []
                            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        # frames not read
        # active mode
        modeType = 0
        counter = 0
    


    #cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance",imgBackground)
    cv2.waitKey(1)