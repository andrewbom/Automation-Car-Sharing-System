import cv2
import sys
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

#load the Haar face detection algorithm
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

#cap = cv2.VideoCapture(0)
print("Starting camera..")
camera = PiCamera()
camera.resolution = (384, 240)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=(384, 240))
#time.sleep(0.5)
print("camera started")

# For each person, one face id
face_id = 1

frame_count = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	#capture image and convert to grayscale
	#print("processing frame :%d" % frame_count)
	image = frame.array
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Detect faces in the image
	faces = faceCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

	# Draw a rectangle around the faces
	for (x, y, w, h) in faces:
		cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
		if len(faces) > 0 :
			print("found %d face at x:%d and y:%d, frame: %d size %d x %d" % (len(faces), x, y, frame_count,  w, h))

	#clean up and display
	rawCapture.truncate(0)
	frame_count = frame_count + 1
	# Save the captured image into the datasets folder
        cv2.imwrite("dataset/User" + str(face_id) + '' + str(frame_count) + ".jpg", gray)
	cv2.imshow("Faces found", image)
	if cv2.waitKey(100) & 0xFF == ord('q'):
		break
	elif frame_count>100:
        	break

#cap.release()
cv2.destroyAllWindows()

def detect_face(image, cascade):
	image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale(image_grayscale, scaleFactor=1.2, minNeighbors=5)
	return faces

