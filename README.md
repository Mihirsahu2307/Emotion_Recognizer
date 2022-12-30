# Emotion_Recognizer
This project is a continuation of my [previous work](https://github.com/Mihirsahu2307/Facial_Emotion_Recognition) where the prediction model was built and trained.
Here, the primiary focus is to develop a webpage that can serve multiple clients and provide them low latency real time predictions from their webcam.

Currently, to use the app, you can clone the repo, and install all required libraries. Then you should run app.py and open localhost:5000.

## TODO:

* Tried using socket programming by passing webcam frames obtained via javascript to server. But the latency is high and the received frames are distorted at times, so alternative approaches are:

1) Build a chrome extension that clients need to download; then all the predictions are done on client side. 
(Not preferred, because then there would be no need of python and users would also have to install an extra extension)

2) Use webRTC to achieve low latency frame transfer to and from server.
