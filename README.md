# Emotion_Recognizer
This project is a continuation of my [previous work](https://github.com/Mihirsahu2307/Facial_Emotion_Recognition) where the prediction model was built and trained.
Here, the primiary focus is to develop a webpage that can serve multiple clients and provide them low latency real time predictions from their webcam.

Demo: [website](http://mihirsahu2307.pythonanywhere.com)

## How to use locally:

* Clone the repo and install the requirements:

```
pip install -r requirements.txt
```

* Run the app using the command:

```
python app.py
```


## Improvements
* Tried using socket programming by passing webcam frames obtained via javascript to server. But the latency is high, so alternative approaches are:

1) Build a chrome extension that clients need to download first; then all the predictions can be done on client side. 
(Not preferred, because then there would be no need of python and users would also have to install an extra extension)

2) Use webRTC to achieve low latency frame transfer to and from server; aiortc is a useful library. However with that approach, flask would have to be discarded.

3) Deployment of webapps that use tensorflow as backend with keras is a real pain. I managed to make it work on pythonanywhere, but maybe another hosting service would serve better, or perhaps there could be a better way to deploy.
