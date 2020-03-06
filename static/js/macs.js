$(document).ready(function() {
    $('.select2').select2();
});

function addMac() {
	var user_id = $("#user_id").val();
	var mac = $("#mac").val();
	var data = new FormData();

	if (user_id == "") {
		alert("Please select a person!");
		return 0;
	}
	if (mac == "") {
		alert("Please specify MAC!");
		return 0;
	}

	data.append('operation', 'add');
	data.append('user_id', user_id);
	data.append('mac', mac);

	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function () {
		if (xhr.readyState == 4) {
			if (xhr.status != 200) {
				alert("Cannot get updated table!");
			} else {
				location.reload(true);
			}
		}
	}
	xhr.open('POST', '/macs', true);
	xhr.send(data);
}

function deleteMac(mac){
  var data = new FormData();
	data.append('operation', 'delete');
	data.append('mac', mac);
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function () {
		if (xhr.readyState == 4) {
			if (xhr.status != 200) {
				alert("Cannot get updated table!");
			} else {
				location.reload(true);
			}
		}
	}
	xhr.open('POST', '/macs', true);
	xhr.send(data);
}
