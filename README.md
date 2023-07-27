# Emotion_Recognizer
This project is a continuation of my [previous work](https://github.com/Mihirsahu2307/Facial_Emotion_Recognition) where the prediction model was built and trained.
Here, the primiary focus is to deploy and scale the model to serve multiple clients and provide them low latency real time predictions from their webcam.

Demo: [website](https://emotion-recognizer.site)

## How to use locally:

* Manual set up:
    * Clone the repo and install the requirements:

    ```
    pip install -r requirements.txt
    ```

    * Run the app using the command:

    ```
    python app.py
    ```

* For scaling with docker, use:

```
docker-compose up --scale app=3
```

## Improvements

* One major improvement was made by shifting some of the image processing steps to the client side. Adding rectangle and text to the image is now done on the client's browser. The advantage is now the server doesn't need to those minor processing steps and it also doesn't need to send the processed image back to client. Instead a json object is passed containing coordinates and emotion status. This reduces latency and the quality of the prediction image on client's browser.
 
* The ML model is separated from the front end and deployed as an API on AWS EC2 instance using gunicorn and nginx. FPS improved by 300%. This allows for horizontal scaling as well.


Further improvements can be made by:

1) Using webRTC to achieve low latency frame transfer to server; aiortc is a useful library. That will make the API non-restful but it should work much faster.

2) ~~Deployment of webapps that use tensorflow as backend with keras is a real pain. I managed to make it work on pythonanywhere, but maybe another hosting service would serve better, or perhaps there could be a better way to deploy.~~

Now, the backend ML model is deployed as an API on EC2, completely separated from the hosted website.


## TODO

1) Deploy the model as an api endpoint on some cloud platform and call the model using javascript from the webapp code. [YT](https://www.youtube.com/results?search_query=deploy+ml+model+as+api+on+cloud) (Deploy the ml model and host the webapp separately). Can also look into the aiortc approach, as flask would be needed for the api endpoint anyway. (**DONE** on 13/05/2023)
