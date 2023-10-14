function onUserPermissionChange(user_key, device_id, context) {
    console.log('change permission for user ' + user_key + ' on device ' + device_id);

    var data = new FormData();
	data.append('user_key', user_key);
	data.append('device_id', device_id);

    if (context.checked) {
        method = 'POST';
    } else {
        method = 'DELETE';
    }

    console.log('method: ' + method);

    var xhr = new XMLHttpRequest();
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
	xhr.open(method, '/permission', true);
	xhr.send(data);
}

function onUserDeleteClick(user_key, a) {
    console.log('onUserDeleteClick ' + user_key);

    var data = new FormData();
	data.append('user_key', user_key);

	var xhr = new XMLHttpRequest();
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
	xhr.open('DELETE', '/user', true);
	xhr.send(data);
}

function addUser() {
	var name = $("#user_name").val();
	var key = $("#user_key").val();
	var data = new FormData();

	if (name == "") {
		alert("Please specify nickname!");
		return 0;
	}
	if (key == "") {
		alert("Please specify access key!");
		return 0;
	}

	data.append('nick', name);
	data.append('key', key);

	var xhr = new XMLHttpRequest();
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
