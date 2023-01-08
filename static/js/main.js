$(document).ready(function(){
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    const video = document.querySelector("#videoElement");
    const form = document.getElementById('my-form');
    const but = document.getElementById('SendBtn')

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/requests');
        const data = "Detect Emotion On/Off"
        xhr.send(data);

        but.disabled = true;
        setTimeout(function(){
            but.disabled = false;
        }, 1000);
    });

    video.width = 640;
    video.height = 480; 


    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();

            const FPS = 5;
            setInterval(submitFrame, 1000/FPS);
        })
        .catch(function (error) {
            console.log(error)
        });
    }

    function submitFrame(){
        width=video.width;
        height=video.height;
        context.drawImage(video, 0, 0, width , height );

        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('image', blob);
          
            console.log('Adios')
            fetch("/webcam", {
                method: 'POST',
                body: formData,
            }).then(function(response) {
                return response.blob();
            }).then(function(blob) {
                console.log('Heh, you got me!')
                photo.src = URL.createObjectURL(blob);
            }).catch(function(err) {
                console.log('Fetch problem: ' + err.message);
            });

        }, 'image/jpeg', 0.7);

        context.clearRect(0, 0, width,height );
    }
});