from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit
import time
import io
from PIL import Image
import base64,cv2
import numpy as np
from engineio.payload import Payload
# from prediction_model import *
# from Scheduler import *
import keras.utils

Payload.max_decode_packets = 2048

app = Flask(__name__, template_folder='./templates')
socketio = SocketIO(app,cors_allowed_origins='*' , logger = False)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


global fps, prev_recv_time, face_roi, emotion_detect, fd_model, status, counter

counter = 0
modelFile = "saved_model/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "saved_model/deploy.prototxt.txt"
fd_model = cv2.dnn.readNetFromCaffe(configFile, modelFile)
fps=5
prev_recv_time = 0
emotion_detect = 0
face_roi = np.zeros((3, 3, 3))
status = 'neutral'

#face expression recognizer initialization
from keras.models import model_from_json
model = model_from_json(open("ml_model/facial_expression_model_structure.json", "r").read())
model.load_weights('ml_model/facial_expression_model_weights.h5') #load weights


# Using a different prediction model in this method
def predict():
    global face_roi, status
    classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
    face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) #transform to gray scale
    face_roi = cv2.resize(face_roi, (48, 48)) #resize to 48x48
    img_pixels = keras.utils.img_to_array(face_roi)
    img_pixels = np.expand_dims(img_pixels, axis = 0)
    
    img_pixels /= 255 #pixels are in scale of [0, 255]. normalize all pixels in scale of [0, 1]
    
    predictions = model.predict(img_pixels) #store probabilities of 7 expressions
    
    max_index = np.argmax(predictions[0])
    status = classes[max_index]


# # Original prediction model
# def predict_emotion(save_images = 0):
#     global status, face_roi, emotion_detect, counter
    
#     if not emotion_detect:
#         return
    
#     img_size = 224
#     classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
#     try:
#         final_image = cv2.resize(face_roi, (img_size, img_size))
#         final_image = np.expand_dims(final_image, axis = 0)
            
#         Predictions = model6.predict(final_image)
#         class_num = np.argmax(Predictions)   # **Provides the index of the max argument
        
#         status = classes[class_num]
#     except:
#         pass
    
#     print("Emotion: ", status)

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

# rt = Scheduler(0.5, predict_emotion, 0) # Call predict every x seconds

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
        # print("here")
        global emotion_detect
        emotion_detect =not emotion_detect
        # if request.form.get('detect_emotion') == 'Detect Emotion On/Off':
            
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app,port=9990 ,debug=True)
