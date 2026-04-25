function checkLocation() {
    navigator.geolocation.getCurrentPosition(pos => {

        fetch("/check-location/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                lat: pos.coords.latitude,
                lng: pos.coords.longitude
            })
        })
        .then(res => res.json())
        .then(data => {

            if (data.status === "inside") {
                const box = document.getElementById("message-box");
                box.classList.remove("d-none");
                box.innerHTML = `
                    <b>📨 رسالة:</b><br>
                    ${data.message}
                `;
            }
        });

    }, err => {
        document.getElementById("status").innerHTML = "⚠️ لا يمكن تحديد موقعك";
    });
}

setInterval(checkLocation, 5000);