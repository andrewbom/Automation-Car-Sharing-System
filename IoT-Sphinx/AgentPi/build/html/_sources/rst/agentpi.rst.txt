====
MAIN
====

.. code-block:: python

import socket
import threading
import os
import sys
from getpass import getpass
import time
from recognition import Recognition
from pick import pick
from location_use_case import Car_location


data = ""
connected = False
count = 1
progress = "."
start_time = time.time()

# Attempt connection to server of the master pi
while not connected:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # local host of the master pi
        sock.connect(("192.168.0.3", 5001))
        connected = True
        print("Successfully connected to Master Pi Server")
        time.sleep(5)

        # Wait for the incoming data from Master Pi server
        # .decode is used to turn the message from bytes to a string
        def receive(socket, signal):
            # if there is a signal, run the following coding
            while signal:
                try:
                    # receiving the data from agent_pi
                    data = socket.recv(200)
                    print("\n")
                    print(str(data.decode("utf-8")))
                    print("\n")

                except:
                    # show the message that signal is disconnected
                    print("You have been disconnected from the server")
                    signal = False
                    break

        # Function to gain the Mac address that connected to the raspberry pi (agent pi) from location_use_case.py
        # The gained value represents the address of the raspberry pi (agent pi) and send to master pi
        def location_update():
            map_initial_time = time.time()
            while connected:
                new_map_time = time.time() - map_initial_time

                # refresh the location data every minute
                if new_map_time >= 10:
                    locate = Car_location()

                    # Getting the latitude and longitude value of Mac
                    loc_data = locate.Get_Location()

                    # encode the location data and send it to Master pi
                    sock.sendall(str.encode(loc_data))
                    map_initial_time = time.time()


        # Create new thread to wait for data and wait for location update
        receiveThread = threading.Thread(target=receive, args=(sock, True))
        receiveThread.start()
        locationThread = threading.Thread(target=location_update)
        locationThread.start()

        # Loop for menu of agent pi in console and collect user inputs
        while True:
            clear = lambda: os.system('clear')
            title = 'Please select an option: '
            options = ['Unlock Booked Car', 'Return Car']
            option, index = pick(options, title)
            print(option)
            print("##########")
            print("########## \n")

            # if the option is 'Unlock Booked Car'
            if index == 0:
                status = "collected"

                title = 'Please select an authorization option: '
                options = ['use username and password', 'use face recognition']
                option, index = pick(options, title)
                print(option)
                print("##########")
                print("########## \n")

                # if the option is 'use username and password'
                if index == 0:
                    username = input("Insert Username :")
                    print("\n")

                    password = getpass("Insert password :")
                    print("\n")

                    customer_id = input("Insert your Customer ID :")
                    print("\n")

                    car_id = input("Insert Car ID :")
                    print("\n")

                    message = '{"type": "credentials", "status": "%s", "username": "%s", "password": "%s", "customer_id": "%s", "car_id": "%s"}' % (
                        status, username, password, customer_id, car_id)

                    # sending back the credentials data to Master Pi for data validation
                    # Master Pi will return the message of validation result
                    sock.sendall(str.encode(message))
                    time.sleep(10)
                    clear()

                # if the option is 'use face recognition'
                elif index == 1:
                    recog = Recognition()
                    data = recog.start_recognition(status)
                    sock.sendall(str.encode(data))
                    time.sleep(10)
                    clear()

            # if the option is 'Return Car'
            elif index == 1:
                status = "returned"
                title = 'Please select an authorization option: '
                options = ['use username and password', 'use face recognition']
                option, index = pick(options, title)
                print(option)
                print("##########")
                print("########## \n")

                # if the option is 'use username and password'
                if index == 0:
                    username = input("Insert Username :")
                    print("\n")

                    password = getpass("Insert password :")
                    print("\n")

                    customer_id = input("Insert your Customer ID :")
                    print("\n")

                    car_id = input("Insert Car ID :")
                    print("\n")

                    message = '{"type": "credentials", "status": "%s", "username": "%s", "password": "%s", "customer_id": "%s", "car_id": "%s"}' % (
                        status, username, password, customer_id, car_id)

                    # sending back the credentials data to Master Pi for data validation
                    # Master Pi will return the message of validation result
                    sock.sendall(str.encode(message))
                    time.sleep(10)
                    clear()

                # if the option is 'use face recognition'
                elif index == 1:
                    recog = Recognition()
                    data = recog.start_recognition(status)
                    sock.sendall(str.encode(data))
                    time.sleep(10)
                    clear()

    # if the agent pi still attempts to build the connection to server of the master pi
    except:
        newtime = time.time() - start_time

        # if the connection time has exceeded more than 3 seconds
        if newtime >= 3:
            # flush the "." which represents the number of attempt that connect to the master pi
            count += 1
            sys.stdout.write("Trying to connect: %s \r" % (progress * count))
            sys.stdout.flush()
            start_time = time.time()

===========
RECOGNITION
===========

.. code-block:: python

import cv2
import time
import json
from database_utils import Database_utils


class Recognition:
    def __init__(self):
        # Create Local Binary Patterns Histograms for face recognition
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        # Loading model
        self.recognizer.read('/home/pi/Projects/agentpi/trainer/trainer.yml')
        # Load the haarcascade Frontal Face model
        self.cascadePath = "/home/pi/Projects/agentpi/haarcascade_frontalface_default.xml"

    def start_recognition(self, status):
        # Create classifier from pre-built model
        faceCascade = cv2.CascadeClassifier(self.cascadePath)
        # Set the font style
        font = cv2.FONT_HERSHEY_SIMPLEX
        print("Starting camera..")
        # Starting the usb camera that connected to agent pi
        camera = cv2.VideoCapture(0)
        print("camera started")
        print("Please align your face")

        DataTosend = {}

        # Loop for detecting face
        while True:
            ret, image = camera.read()
            if ret:
                # capture image and convert to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Detect faces in the image
                faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

                # Draw a rectangle around the detected faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # Recognize the face belongs to which face ID
                    face_id, conf = self.recognizer.predict(gray[y:y + h, x:x + w])

                    # Check if the face ID exists in the local database
                    if face_id:
                        db = Database_utils()
                        # if existed, fetch the data
                        userdata = db.get_face_data(face_id)
                        # fetch the car information that the agent pi attaches to
                        cardata = db.get_car_data()

                        # If user with the face ID is present, return user data to main
                        if userdata is not None:
                            username = userdata[1]
                            password = userdata[2]
                            customer_id = userdata[3]
                            car_id = cardata[1]

                            data = {
                                "type": "credentials",
                                "status": status,
                                "username": username,
                                "password": password,
                                "customer_id": customer_id,
                                "car_id": car_id,
                            }
                            DataTosend = json.dumps(data)

                            # if the face has matched with the local database, show the information
                            cv2.putText(image, str(username), (50, 50), font, 2, (255, 255, 255), 3)

                        # If user with the face ID is NOT existed, return fail message to main
                        elif userdata is None:
                            face_id = "Unknown"
                            # Put text describe who is in the picture
                            cv2.putText(image, str(face_id), (50, 50), font, 2, (255, 255, 255), 3)

                            data = {"type": "face recog fail"}
                            DataTosend = json.dumps(data)

            # set the window for displaying the camera
            cv2.imshow("Faces found", image)

            # wait for the user to press the key "q" to quit for face recognition process
            if cv2.waitKey(100) & 0xFF == ord('q'):
                # if the face recognition process ends, close the camera and its window
                camera.release()
                cv2.destroyAllWindows()
                return DataTosend

=======
CAPTURE
=======

.. code-block:: python

import cv2
from database_utils import Database_utils

cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# prompt user input for account information
name = input('enter your Name: ')
email = input('enter your email: ')
password = input('enter your password: ')
customer_id = input('enter your customer id: ')
face_id = customer_id  # face_id will be assigned same as customer_id
sampleNum = 0

# saving the user input to local database
db = Database_utils()
db.insert_account(email, password, customer_id, face_id)

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # incrementing sample number
        sampleNum = sampleNum + 1
        # saving the captured face in the dataset folder
        cv2.imwrite("/home/pi/Projects/agentpi/data/raw/" + name + "." + face_id + '.' + str(sampleNum) + ".jpg",
                    gray[y:y + h, x:x + w])

    cv2.imshow('frame', img)
    # wait for 100 miliseconds
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    # break if the sample number is more than 20
    elif sampleNum > 20:
        break

cam.release()
cv2.destroyAllWindows()

=================
LOCATION_USE_CASE
=================

.. code-block:: python

import uuid
import requests
import json
from database_utils import Database_utils
import math


# This class reads the mac address and sends it to the google geolocation API.
# The API returns latitude and longitude of the Mac address which is connecting with the raspberry pi.
# The latitude and longitude is therefore representing the address of the raspberry pi (agent pi) and send to master pi
class Car_location:

    def __init__(self):
        # print ("The MAC address in formatted way is : ", end="")
        self.mac_address = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                      for ele in range(0, 8 * 6, 8)][::-1]))

        self.URL = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCntWQD7A7rjkkwSi0-5ehvZt_eg3_6Dqs"

    def truncate(self, number, digits) -> float:
        multiplier = 10.0 ** digits
        return math.trunc(multiplier * number) / multiplier

    def Get_Location(self):
        headers = {
            'Content-type': 'application/json',
        }

        PARAMS = {
            "macAddress": self.mac_address,
            "signalStrength": -43,
            "age": 0,
            "channel": 11,
            "signalToNoiseRatio": 0
        }

        data = json.dumps(PARAMS)

        # sending get request and saving the response as response object
        r = requests.post(url=self.URL, headers=headers, data=data)

        data = json.loads(r.text)
        latitude = (data['location']['lat'])
        longitude = (data['location']['lng'])

        # get the car information from local database
        db = Database_utils()
        cardata = db.get_car_data()
        car_id = cardata[1]

        location_data = {
            "type": "location",
            "car_id": car_id,
            "latitude": self.truncate(latitude, 7),
            "longitude": self.truncate(longitude, 7)
        }
        dataTosend = json.dumps(location_data)

        db.update_car_location(latitude, longitude)
        return dataTosend

==============
DATABASE_UTILS
==============

.. code-block:: python

import sqlite3
from sqlite3 import Error


class Database_utils:
    def __init__(self, connection=None):
        self.database_name = 'agentpi_db'
        self.con = self.sql_connection()
        self.sql_initialize()

    def sql_initialize(self):
        self.sql_table()
        self.sql_insert_data()

    def sql_connection(self):
        try:
            con = sqlite3.connect(self.database_name)
            return con

        except Error:
            print(Error)

    def sql_table(self):
        cursorObj = self.con.cursor()

        cursorObj.execute("""
             DROP TABLE IF EXISTS car_details
        """)

        # Create a car details' TABLE in the local database
        cursorObj.execute("""
            CREATE TABLE IF NOT EXISTS car_details(
                id integer PRIMARY KEY,
                car_id real,
                make_name text,
                model_name text,
                seating_capacity real, 
                colour text, 
                car_type text,
                registration_no real,
                lat real ,lng real)
        """)

        # Create a user details' TABLE in the local database
        cursorObj.execute("""
            CREATE TABLE IF NOT EXISTS user_details(
                id integer PRIMARY KEY, 
                username text, 
                password text,
                customer_id integer,
                face_id integer)
        """)
        self.con.commit()

    def sql_insert_data(self):
        cursorObj = self.con.cursor()

        # Set 1 Car information that connected to 1 agent pi in the local database
        cursorObj.execute("INSERT INTO car_details(car_id , make_name ,model_name ,seating_capacity, colour, car_type ,registration_no ,lat ,lng ) VALUES (1 ,'Sedan' ,'Toyota' ,4 ,'red' ,'suv' ,32 ,-9 ,-9 )")

        self.con.commit()

    def insert_account(self, email, password, customer_id, face_id):
        cursorObj = self.con.cursor()
        cursorObj.execute("INSERT INTO user_details(username, password, customer_id, face_id) VALUES (?, ?, ?, ?)", (email, password, customer_id, face_id))
        self.con.commit()

    def update_car_location(self, lat, lng):
        cursorObj = self.con.cursor()
        cursorObj.execute('UPDATE car_details SET lat = {} and lng = {} where id = 1'.format(lat, lng))
        self.con.commit()

    def get_car_data(self):
        cursorObj = self.con.cursor()
        cursorObj.execute('SELECT * FROM car_details')
        return cursorObj.fetchone()

    def get_face_data(self, face_id):
        cursorObj = self.con.cursor()
        cursorObj.execute('SELECT * FROM user_details WHERE face_id = {}'.format(face_id))
        return cursorObj.fetchone()

    def get_user_data(self):
        cursorObj = self.con.cursor()
        cursorObj.execute('SELECT * FROM user_details')
        return cursorObj.fetchone()

========
TRAINING
========

.. code-block:: python

# Import OpenCV2 for image processing
# Import os for file path
import cv2, os
import numpy
from PIL import Image

GRAY_FOLDER = os.getcwd() + '/data/dataset/'
RAW_FOLDER = os.getcwd() + '/data/raw/'


def getImagesAndLabels():
    imagePaths = [os.path.join(RAW_FOLDER, f) for f in os.listdir(RAW_FOLDER)]
    # Initialize empty face sample list
    faceSamples = []
    # Initialize empty id list
    ids = []
    print("Training started!")

    # Loop all the file path
    for imagePath in imagePaths:
        # Get the image and convert it to grayscale
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = numpy.array(PIL_img, 'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = cv2.CascadeClassifier("/home/pi/Projects/agentpi/haarcascade_frontalface_default.xml").detectMultiScale(
            img_numpy)

        # Loop for each face, append to their respective ID
        for (x, y, w, h) in faces:
            # Add the image to face samples
            faceSamples.append(img_numpy[y:y + h, x:x + w])
            # Add the ID to IDs
            ids.append(id)

    for image in os.listdir(RAW_FOLDER):
        img = cv2.imread(os.path.join(RAW_FOLDER, image))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(GRAY_FOLDER + "/" + image, img_gray)
        print(image)
        os.remove(os.path.join(RAW_FOLDER, image))

    # Pass the face array and IDs array
    return faceSamples, ids


faces, ids = getImagesAndLabels()
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, numpy.array(ids))
recognizer.write('trainer/trainer.yml')
print("Training completed!")

==========
1_TRAINING
==========

.. code-block:: python

# Import OpenCV2 for image processing
# Import os for file path
import cv2, os
import numpy
from PIL import Image

GRAY_FOLDER = os.getcwd() + '/data/dataset/'
RAW_FOLDER = os.getcwd() + '/data/raw/'


def getImagesAndLabels():
    imagePaths = [os.path.join(RAW_FOLDER, f) for f in os.listdir(RAW_FOLDER)]
    faceSamples = []  # Initialize empty face sample list
    ids = []  # Initialize empty id list
    print("Training started!")

    # Loop all the file path
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')  # Get the image and convert it to grayscale
        img_numpy = numpy.array(PIL_img, 'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = cv2.CascadeClassifier("/home/pi/Projects/agentpi/haarcascade_frontalface_default.xml").detectMultiScale(
            img_numpy)

        # Loop for each face, append to their respective ID
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y + h, x:x + w])  # Add the image to face samples
            ids.append(id)  # Add the ID to IDs

    for image in os.listdir(RAW_FOLDER):
        img = cv2.imread(os.path.join(RAW_FOLDER, image))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(GRAY_FOLDER + "/" + image, img_gray)
        print(image)
        os.remove(os.path.join(RAW_FOLDER, image))

    # Pass the face array and IDs array
    return faceSamples, ids


faces, ids = getImagesAndLabels()
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, numpy.array(ids))
recognizer.write('trainer/trainer.yml')
print("Training completed!")






