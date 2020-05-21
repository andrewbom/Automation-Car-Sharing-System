from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import sys
import time
import json
from database_utils import Database_utils


class Recognition:
    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()  # Create Local Binary Patterns Histograms for face recognization
        self.recognizer.read('/home/pi/Projects/agentpi/trainer/trainer.yml')  # Loading model
        self.cascadePath = "/home/pi/Projects/agentpi/haarcascade_frontalface_alt.xml"  # Load the haarcascade Frontal Face model

    def start_recognition(self, status):
        faceCascade = cv2.CascadeClassifier(self.cascadePath)  # Create classifier from prebuilt model
        font = cv2.FONT_HERSHEY_SIMPLEX  # Set the font style
        print("Starting camera..")
        camera = cv2.VideoCapture(0)
        rawCapture = PiRGBArray(camera, size=(384, 240))
        print("camera started")
        print("Please align your face")

        start_time = time.time()  # Set timer for querrying location of device
        end = False

        # Loop
        while (True):
            ret, image = camera.read()
            if ret:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # capture image and convert to grayscale
                faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)  # Detect faces in the image

                # Draw a rectangle around the faces 
                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)
                    # Recognize the face belongs to which ID
                    id, conf = self.recognizer.predict(gray[y:y + h, x:x + w])

                    # Check the ID if exist in local database
                    if (id):
                        db = Database_utils()
                        userdata = db.get_face_data(id)
                        cardata = db.get_car_data()

                        if (userdata is not None):  # If user with the face ID is present return user data to main
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
                            # print(username)
                            end = True
                            break

                        elif (userdata is None and time.time() - start_time >= 30):
                            print("User Not Found")
                            end = True
                            break

                    else:
                        id = "unknown"
                        # Put text describe who is in the picture
                        cv2.rectangle(image, (x - 30, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
                        cv2.putText(image, str(id), (x, y - 90), font, 2, (255, 255, 255), 3)

            cv2.imshow("Faces found", image)
            cv2.waitKey(1)
            rawCapture.truncate(0)

            if end == True:
                camera.release()
                cv2.destroyAllWindows()
                return (DataTosend)
                break
