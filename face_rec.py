import os
import cv2
import face_recognition
import numpy as np
from tqdm import tqdm
from collections import defaultdict
from imutils.video import VideoStream
import keras
from keras.models import load_model
from matplotlib import pyplot as plt

emotion_dict= {'Angry': 0, 'Sad': 5, 'Neutral': 4, 'Disgust': 1, 'Surprise': 6, 'Fear': 2, 'Happy': 3}

def init():
    face_cascPath = 'haarcascade_frontalface_alt.xml'
    dataset = 'faces'

    face_detector = cv2.CascadeClassifier(face_cascPath)
    emotion_detect = load_model('model_v6_23.hdf5')
    emotion_map = dict((v,k) for k,v in emotion_dict.items())

    print("[LOG] Opening webcam ...")
    video_capture = VideoStream(src=0, resolution=(640, 480)).start()

    print("[LOG] Collecting images ...")
    images = []
    for direc, _, files in tqdm(os.walk(dataset)):
        for file in files:
            if file.endswith("jpg"):
                images.append(os.path.join(direc,file))
    return (face_detector, video_capture, images, emotion_detect, emotion_map) 

def process_and_encode(images):
    # initialize the list of known encodings and known names
    known_encodings = []
    known_names = []
    print("[LOG] Encoding faces ...")

    for image_path in tqdm(images):
        # Load image
        image = cv2.imread(image_path)
        # Convert it from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
     
        # detect face in the image and get its location (square boxes coordinates)
        boxes = face_recognition.face_locations(image, model='hog')

        # Encode the face into a 128-d embeddings vector
        encoding = face_recognition.face_encodings(image, boxes)

        # the person's name is the name of the folder where the image comes from
        name = image_path.split(os.path.sep)[-2]

        if len(encoding) > 0 : 
            known_encodings.append(encoding[0])
            known_names.append(name)

    return {"encodings": known_encodings, "names": known_names}

def detect_and_display(video_capture, face_detector, emotion_detector, data, emotion_map):
        frame = video_capture.read()
        # resize the frame
        frame = cv2.resize(frame, (0, 0), fx=0.6, fy=0.6)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # for each detected face
        for (x,y,w,h) in faces:
            # Encode the face into a 128-d embeddings vector
            encoding = face_recognition.face_encodings(rgb, [(y, x+w, y+h, x)])[0]
            face_image = gray[y:y+h,x:x+w]
            face_image =  cv2.resize(face_image, (48, 48))
            face_image = np.reshape(face_image, [1, face_image.shape[0], face_image.shape[1], 1])
            predicted_class = np.argmax(emotion_detector.predict(face_image))
            predicted_emotion = emotion_map[predicted_class]
            # Compare the vector with all known faces encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)

            # For now we don't know the person name
            name = "Unknown"

            # If there is at least one match:
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number of votes
                name = max(counts, key=counts.get)

            face = frame[y:y+h,x:x+w]
            gray_face = gray[y:y+h,x:x+w]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Display name
            y = y - 15 if y - 15 > 15 else y + 15
            cv2.putText(frame, name + '_' + predicted_emotion, (x, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)

        return frame


if __name__ == "__main__":
    (face_detector, video_capture, images, emotion_detector, emotion_map) = init()
    data = process_and_encode(images)

    while True:
        frame = detect_and_display(video_capture, face_detector, emotion_detector, data, emotion_map)
        cv2.imshow("Face Liveness Detector", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    video_capture.stop()