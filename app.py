from flask import Flask, render_template, request
from flask_socketio import SocketIO
from PIL import Image
import base64,cv2
import numpy as np
from engineio.payload import Payload
from prediction_model import *

Payload.max_decode_packets = 2048


# Bug that took me forever to debug during deployment: Client and server side socketio versions should be compatible

app = Flask(__name__, template_folder='./templates')
# socketio = SocketIO(app, cors_allowed_origins='*', logger = True, engineio_logger = True)
socketio = SocketIO(app, cors_allowed_origins='*')


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


global fps, prev_recv_time, face_roi, emotion_detect, fd_model, status, counter

counter = 0
modelFile = "face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "face_detection_model/deploy.prototxt.txt"
fd_model = cv2.dnn.readNetFromCaffe(configFile, modelFile)
fps=5
prev_recv_time = 0
emotion_detect = 0
face_roi = np.zeros((3, 3, 3))
status = 'neutral'

@socketio.on('connect')
def test_connect():
    print("socket connected")
    
    
def predict():
    global status, face_roi, emotion_detect
    
    if not emotion_detect:
        return
    
    img_size = 224
    classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

    try:
        final_image = cv2.resize(face_roi, (img_size, img_size))
        final_image = np.expand_dims(final_image, axis = 0)
            
        Predictions = model.predict(final_image)
        class_num = np.argmax(Predictions)   # **Provides the index of the max argument
        
        status = classes[class_num]
    except:
        pass
    

def detect_face(frame):
    global fd_model, face_roi
    
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
    
    return (frame, x, y)

@app.route('/webcam', methods = ['POST'])
def process_image():
    global prev_recv_time, fps_array, counter, status
    
    # recv_time = time.time()
    # client to server via xmlhttp
    image = request.files['image']
    
    img = Image.open(image)
    img = np.array(img)
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    
    frame = cv2.flip(frame,1)
    try:
        frame, x, y = detect_face(frame)
        if counter == 4:
            if(emotion_detect and x > -1 and y > -1):
                # predict_emotion()  
                predict()
            counter = 0
        else:
            pass
        counter += 1
        
        if emotion_detect:
            cv2.putText(frame, status, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    except:
        pass
    
    
    # server to js via socketio
    imgencode = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY,40])[1]
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpeg;base64,'
    stringData = b64_src + stringData
    socketio.emit('response_back', stringData)
    
    # try:
    #     fps = 1/(recv_time - prev_recv_time)
    # except ZeroDivisionError as e:
    #     pass
    # prev_recv_time = recv_time
    # print(int(fps))
    
    return render_template('index.html')
    

@app.route('/requests',methods=['POST'])
def user_input():
    if request.method == 'POST':
        global emotion_detect
        emotion_detect =not emotion_detect
            
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app,port=5000 ,debug=True)
