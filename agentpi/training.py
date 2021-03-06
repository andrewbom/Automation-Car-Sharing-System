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
