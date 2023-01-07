from flask import Flask, render_template, request, make_response
import cv2
import numpy as np
from prediction_model import *

# Bug that took me forever to debug during deployment: Client and server side socketio versions should be compatible
# Better solution: Just discard socketio completely and use javascript fetch()
app = Flask(__name__, template_folder='./templates')

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
    
def predict():
    global status, face_roi, emotion_detect
    
    if not emotion_detect:
        return
    
    img_size = 224
    classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

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

def send_file_data(data, mimetype='image/jpeg', filename='output.jpg'):
    response = make_response(data)
    response.headers.set('Content-Type', mimetype)
    response.headers.set('Content-Disposition', 'attachment', filename=filename)

    return response

@app.route('/webcam', methods = ['GET', 'POST'])
def process_image():
    global prev_recv_time, counter, status
    
    image = request.files.get('image')
    try:
        frame = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_UNCHANGED)
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
    except:
        pass
    
    
    print('Processed 1 frame')
    buf = cv2.imencode('.jpg', frame)[1]
    return send_file_data(buf.tobytes())
    

@app.route('/requests',methods=['POST'])
def user_input():
    if request.method == 'POST':
        global emotion_detect
        emotion_detect =not emotion_detect
        print("Detect Emotion: ", emotion_detect)
            
    return render_template('index.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000 ,debug=True)

