function onCheckboxChange(context) {
	var data = new FormData();
	data.append('operation', 'edit');
	data.append('id', context.value.split(",")[1]);
	data.append('device', context.value.split(",")[0]);
	data.append('state', context.checked);

	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function () {
		if (xhr.readyState == 4) {
			if (xhr.status != 200) {
				alert("Cannot get updated table!");
			}
		}
	}
	xhr.open('POST', '/', true);
	xhr.send(data);
}

function onDeleteClick(id_value) {
	var data = new FormData();
	data.append('operation', 'delete');
	data.append('id', id_value);
	data.append('device', '');
	data.append('state', '');

	console.log(id_value);
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
	xhr.open('POST', '/', true);
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

	data.append('operation', 'add');
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
	xhr.open('POST', '/', true);
	xhr.send(data);
}
