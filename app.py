from flask import Flask, render_template, request, make_response
import cv2
import numpy as np
from prediction_model import *

# Bug that took me forever to debug during deployment: Client and server side socketio versions should be compatible
# Better solution: Just discard socketio completely and use javascript fetch()

app = Flask(__name__, template_folder='./templates')

modelFile = "face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "face_detection_model/deploy.prototxt.txt"
fd_model = cv2.dnn.readNetFromCaffe(configFile, modelFile)

def predict(face_roi):
    img_size = 224
    classes = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
    status = 'Neutral'

    try:
        final_image = cv2.resize(face_roi, (img_size, img_size))
        final_image = np.expand_dims(final_image, axis = 0)
            
        print('Now predicting...')
        Predictions = model.predict(final_image)
        class_num = np.argmax(Predictions)   # **Provides the index of the max argument
        
        print('Done predicting')
        status = classes[class_num]
    except:
        pass
    
    return status

def detect_face(frame):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
        (300, 300), (104.0, 177.0, 123.0))   
    fd_model.setInput(blob)
    detections = fd_model.forward()
    confidence = detections[0, 0, 0, 2] # atmost 1 face detected

    if confidence < 0.5:            
        return (frame, -1, -1)           

    box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
    (x, y, x1, y1) = box.astype("int")
    face_roi = np.zeros((3, 3, 3))
    try:
        # dim = (h, w)
        face_roi = frame[y:y1, x:x1]
        cv2.rectangle(frame, (x, y), (x1, y1), (0, 0, 255), 2)
        (h, w) = frame.shape[:2]
        r = 480 / float(h)
        dim = ( int(w * r), 480)
        frame=cv2.resize(frame,dim)
    except Exception as e:
        raise
    
    return (frame, face_roi, x, y, x1, y1)

def send_file_data(data, mimetype='image/jpeg', filename='output.jpg'):
    response = make_response(data)
    response.headers.set('Content-Type', mimetype)
    response.headers.set('Content-Disposition', 'attachment', filename=filename)

    return response

@app.route('/face', methods = ['GET', 'POST'])
def process_image1():
    image = request.files.get('image')
    x = 0
    y = 0
    x1= 0
    y1 = 0
    try:
        frame = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        # frame = cv2.flip(frame,1)
        frame, _, x, y, x1, y1 = detect_face(frame)
    except:
        pass
    
    w = x1 - x
    h = y1 - y
    
    response = {
        'x' : int(x), 
        'y' : int(y),
        'w' : int(w),
        'h' : int(h)
    }
    return response

@app.route('/emotion', methods = ['GET', 'POST'])
def process_image2():
    image = request.files.get('image')
    x = 0
    y = 0
    x1= 0
    y1 = 0
    status = 'Neutral'
    try:
        frame = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        # frame = cv2.flip(frame,1)
        frame, face_roi, x, y, x1, y1 = detect_face(frame)
        status = predict(face_roi)
        # cv2.putText(frame, status, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    except:
        pass
    
    w = x1 - x
    h = y1 - y
    
    response = {
        'x' : int(x), 
        'y' : int(y),
        'w' : int(w),
        'h' : int(h),
        'status' : status
    }
    return response

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000 ,debug=True)