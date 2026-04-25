let video = document.getElementById("camera");
let canvas = document.getElementById("snapshot");
let ctx = canvas.getContext("2d");

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        });
}

function captureFrame() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    let imageData = canvas.toDataURL("image/jpeg");

    fetch("/verify-gesture/", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            window.location.href = "/leader/dashboard/";
        }
    });
}

setInterval(captureFrame, 1500);
startCamera();