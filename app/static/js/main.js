$(document).ready(function(){

    // 2 canvas are used, one for the webcam and another for processing the prediction image
    // reason is, the same canvas shouldn't be used in the callback of the toBlob() of the canvas (glitches)
    
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    var canvas_op = document.getElementById('canvasOutput');
    var context_op = canvas_op.getContext('2d');
    context_op.font = 'italic 25px Arial';
    context_op.fillStyle = 'white';

    const gradient = context_op.createLinearGradient(0, 0, 170, 0);
    gradient.addColorStop("0", "magenta");
    gradient.addColorStop("0.5" ,"blue");
    gradient.addColorStop("1.0", "red");
    context_op.lineWidth = 2;

    const video = document.querySelector("#videoElement");
    const form = document.getElementById('my-form');
    const but = document.getElementById('SendBtn')

    var counter = 0; // counts frames
    var detect_emotion = 0; // boolean to detect emotion
    var status = "Neutral"; // emotion status

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        detect_emotion = 1 - detect_emotion;

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

            const FPS = 8;
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

            counter = counter + 1;
            console.log('Adios')

            if(detect_emotion && counter == 3) {
                fetch("/emotion", {
                    method: 'POST',
                    body: formData,
                }).then(function(response) {
                    return response.json();
                }).then(function(_response) {
                    console.log('Heh, you got me!')

                    x = _response.x;
                    y = _response.y;
                    w = _response.w;
                    h = _response.h;
                    status = _response.status;
                    context_op.drawImage(video, 0, 0, width, height);
                    if(x > -1 && y > -1) {
                        ctx.strokeStyle = gradient;
                        context_op.strokeRect(x, y, w, h);
                        context_op.fillText(status, x, y);
                    }

                    canvas_op.toBlob(function(blob_) {
                        photo.src = URL.createObjectURL(blob_);
                    });

                    context_op.clearRect(0, 0, width, height);
                }).catch(function(err) {
                    console.log('Fetch problem: ' + err.message);
                });
                counter = 0;
            }
            else {
                fetch("/face", {
                    method: 'POST',
                    body: formData,
                }).then(function(response) {
                    return response.json();
                }).then(function(_response) {
                    console.log('Heh, you got me!')
                    x = _response.x;
                    y = _response.y;
                    w = _response.w;
                    h = _response.h;

                    context_op.drawImage(video, 0, 0, width, height);
                    if(x > -1 && y > -1) {
                        // for some reason context.stroke() rectangles will remain on the canvas even after clearRect is called
                        // so replaced it with strokeRect
                        context_op.strokeStyle = gradient;
                        context_op.strokeRect(x, y, w, h);

                        if(detect_emotion) {
                            context_op.fillText(status, x, y);
                        }
                    }

                    canvas_op.toBlob(function(blob_) {
                        photo.src = URL.createObjectURL(blob_);
                    });

                    context_op.clearRect(0, 0, width, height);
                }).catch(function(err) {
                    console.log('Fetch problem: ' + err.message);
                });
            }

            if(counter == 3) {
                counter = 0;
            }
        }, 'image/jpeg', 0.7);

        context.clearRect(0, 0, width,height );
    }
});