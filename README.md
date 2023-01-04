# Emotion_Recognizer
This project is a continuation of my [previous work](https://github.com/Mihirsahu2307/Facial_Emotion_Recognition) where the prediction model was built and trained.
Here, the primiary focus is to develop a webpage that can serve multiple clients and provide them low latency real time predictions from their webcam.

## How to use:

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

2) Use webRTC to achieve low latency frame transfer to and from server; aiortc is a useful library. However with that approach, flask will have to be discarded.
