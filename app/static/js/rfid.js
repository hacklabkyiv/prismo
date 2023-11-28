function onUserPermissionChange(user_key, device_id, context) {
    console.log('change permission for user ' + user_key + ' on device ' + device_id);

    let data = new FormData();
    data.append('user_key', user_key);
    data.append('device_id', device_id);

    if (context.checked) {
        method = 'POST';
    } else {
        method = 'DELETE';
    }

    console.log('method: ' + method);

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status != 200) {
                alert("Cannot get updated table!");
            } else {
                location.reload();
            }
        }
    }
    xhr.open(method, '/permission', true);
    xhr.send(data);
}

function onUserDeleteClick(user_key, a) {
    console.log('onUserDeleteClick ' + user_key);

    let data = new FormData();
    data.append('user_key', user_key);

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status != 200) {
                alert("Cannot get updated table!");
            } else {
                // Reload page when we received response
                location.reload();
            }
        }
    }
    xhr.open('DELETE', '/user', true);
    xhr.send(data);
}

function addUser(user_key, user_name) {
    let data = new FormData();

    if (user_name == "") {
        alert("Please specify nickname!");
        return 0;
    }
    if (user_key == "") {
        alert("Please specify access key!");
        return 0;
    }

    data.append('nick', user_name);
    data.append('key', user_key);

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status != 200) {
                alert("Cannot get updated table!");
            } else {
                // Reload page when we received response
                location.reload(true);
            }
        }
    }
    xhr.open('POST', '/user', true);
    xhr.send(data);
}

function addDevice() {
    console.log("Add device called");
    let device_name = $("#device_name").val();
    let device_id = $("#device_id").val();
    let data = new FormData();

    if (device_name == "") {
        alert("Please specify device_name!");
        return 0;
    }
    if (device_id == "") {
        alert("Please specify device_id!");
        return 0;
    }

    data.append('device_name', device_name);
    data.append('device_id', device_id);

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status != 200) {
                alert("Cannot get updated table!");
            } else {
                // Reload page when we received response
                location.reload(true);
            }
        }
    }
    xhr.open('POST', '/device', true);
    xhr.send(data);

    console.log(data);
}
