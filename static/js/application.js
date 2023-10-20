function flashFirmware() {
    console.log("Test!");
    const socket = new WebSocket('ws://' + location.host + '/updater_socket');
    const log = (text, color) => {
        document.getElementById('flashLog').innerHTML += `<span style="color: ${color}">${text}</span><br>`;
    };

    socket.addEventListener('message', ev => {
    log('<<< ' + ev.data, 'blue');
    });
}
