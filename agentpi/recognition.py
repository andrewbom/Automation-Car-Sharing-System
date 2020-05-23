import cv2
import sys
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

        # Set timer for querying location of device
        start_time = time.time()
        end = False
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
                    # cv2.rectangle(image, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)
                    # Recognize the face belongs to which face ID
                    face_id, conf = self.recognizer.predict(gray[y:y + h, x:x + w])

                    # if conf < 50:
                    # Check if the face ID exists in the local database
                    if face_id:
                        db = Database_utils()
                        # if existed, fetch the data
                        userdata = db.get_face_data(face_id)
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
                            # wait for the user to press the key "q" to quit for face recognition process
                            # if cv2.waitKey(10) & 0xFF == ord('q'):
                            # end = True
                            # break

                        # If the face ID is NOT existed and the face recognition process has exceeded >= 30 secs
                        # elif userdata is None and time.time() - start_time >= 10:
                        elif userdata is None:
                            face_id = "Unknown"
                            # Put text describe who is in the picture
                            cv2.putText(image, str(face_id), (50, 50), font, 2, (255, 255, 255), 3)

                            data = {"type": "face recog fail"}
                            DataTosend = json.dumps(data)

            # set the window for displaying the camera
            cv2.imshow("Faces found", image)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                # rawCapture.truncate(0)

                # if the face recognition process ends, close the camera and its window
                # if end:
                camera.release()
                cv2.destroyAllWindows()
                return DataTosend
