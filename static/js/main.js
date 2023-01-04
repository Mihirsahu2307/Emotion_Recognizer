$(document).ready(function(){
    var socket = io()
    // var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', function(){
        console.log("Connected...!", socket.connected)
    });

    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    const video = document.querySelector("#videoElement");
    const form = document.getElementById('my-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/requests');
        const data = "Detect Emotion On/Off"
        xhr.send(data);
    });

    video.width = 640;
    video.height = 480; 


    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function (err0r) {

        });
    }

    const FPS = 5;
    setInterval(() => {
        width=video.width;
        height=video.height;
        context.drawImage(video, 0, 0, width , height );

        canvas.toBlob(function(blob) {
            // Now, we can use the Blob object to create a FormData object
            const formData = new FormData();
            formData.append('image', blob);
          
            // Next, we can send the FormData object to the Python server using an HTTP POST request
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/webcam', true);
            xhr.send(formData);
          }, 'image/jpeg', 0.7);

          context.clearRect(0, 0, width,height );
    }, 1000/FPS);


    socket.on('response_back', function(image){
            photo.setAttribute('src', image );
    });
});