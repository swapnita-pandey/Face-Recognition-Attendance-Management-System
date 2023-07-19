import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://facerecognitionattendanc-b5522-default-rtdb.firebaseio.com/"
})


ref = db.reference('Students')

# data dictinary containing student information
data = {
    "321654":
        {
            "name": "Swapnita Pandey",
            "major": "CSE",
            "starting_year": 2020,
            "total_attendance": 7,
            "standing": "B",
            "year": 3,
            "last_attendance_time": "2023-07-14 00:54:34"
        },
    "852741":
        {
            "name": "PM Mr. Namrendra Modi",
            "major": "Political Science",
            "starting_year": 2020,
            "total_attendance": 12,
            "standing": "B",
            "year": 4,
            "last_attendance_time": "2023-07-14 00:54:34"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 7,
            "standing": "A",
            "year": 2,
            "last_attendance_time": "2023-07-14 00:54:34"
        },
    "2017078":
        {
            "name": "Reeta Pandey",
            "major": "Electrical",
            "starting_year": 2018,
            "total_attendance": 12,
            "standing": "B",
            "year": 2,
            "last_attendance_time": "2023-07-14 00:54:34"
        },
    "20022815":
        {
            "name": "H.K. Pandey",
            "major": "Mechanical",
            "starting_year": 2016,
            "total_attendance": 10,
            "standing": "A",
            "year": 1,
            "last_attendance_time": "2023-07-14 00:54:34"
        }
}

# sending the data to firebase database
for key, value in data.items():
    ref.child(key).set(value)