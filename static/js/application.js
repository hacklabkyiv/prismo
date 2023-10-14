
function addUser() {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/tablemgr');
    var nickname = $("#nickname").val();
    var macaddress = $("#macaddress").val();

    if (nickname == "") {
        alert("Please specify nickname!");
        return 0;
    }
    if (macaddress == "") {
        alert("Please specify MAC address!");
        return 0;
    }
    socket.emit('adduser', {
        macaddress: macaddress,
        nickname: nickname
    });
};
