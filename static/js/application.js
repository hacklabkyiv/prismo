/**
 * Javascript part of Hacklab Admin Panel.
 * includes SocketIO communication with backend and
 * implementation of general visual logic
 * 
 * TODO:
 *    * Implement save, discard, delete logic for user data table
 *    * Add comments for functions
 *    * Code review
 */
var DELETE_EDIT_BUTTON_GROUP = '<td class="buttonToolbox">' +
    '<div class="btn-group"><a class="btn btn-danger btn-sm" onclick="deleteRow(this)">' +
    '<i class="fa fa-trash-o"></i></a>' +
    '<a class="btn btn-info btn-sm" onclick="editRow(this)">' +
    '<i class="fa fa-pencil"></i></a></div></td>';

var DISCARD_APPLY_BUTTON_GROUP = '<div class="btn-group">' +
    '<a class="btn btn-danger btn-sm" onclick="discardChanges(this)">' +
    '<i class="fa fa-undo" aria-hidden="true"></i></a>' +
    '<a class="btn btn-primary btn-sm" onclick="applyChanges(this)">' +
    '<i class="fa fa-floppy-o" aria-hidden="true"></i></a></div>';

var MAC_CONVERSION_SERVICE = "http://192.168.1.1/cgi-bin/mac";

var macs = [];

$(function() {
  $.getJSON( MAC_CONVERSION_SERVICE, function( data ) {
    macs = data.macs;
  });
});

$(function() {
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/log');
    var msgReceived = [];

    //receive details from server
    socket.on('newmessage', function(msg) {
        msgReceived.push(msg);
        numbers_string = '';
        // TODO: Maybe here we could use append function?
        $('#log').html(numbers_string);
        for (var i = 0; i < msgReceived.length; i++) {
            numbers_string = numbers_string + msgReceived[i] + '<br>';
            console.log(i);
        }
        $('#log').html(numbers_string);
    });

});

$(function() {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/tablemgr');
    socket.on('tabledata', function(msg) {
        var table_data = JSON.parse(msg);
        var index;
        $("#table_body").empty();
        $("#table_full_status_body").empty();
        for (index = 0; index < table_data.length; ++index) {
            console.log(table_data[index]);
            addTableRow(table_data[index]);
        }
    });
});

function addTableRow(data) {
    if (data.hasOwnProperty('id')) {
        var decorated = (data.status == 'online' ? '<strong>online</strong>' : 'offline');
        $("#tblData tbody").append(
            "<tr>" +
            '<td class="id_entry">' + data.id + "</td>" +
            '<td class="mac_entry" data-mac="' + data.mac + '">' + 
            data.mac.replace(/;/g, '<br>') + "</td>" +
            '<td class="status_entry">' + decorated + "</td>" +
            '<td class="nick_entry">' + data.nick + "</td>" +
            DELETE_EDIT_BUTTON_GROUP +
            "</tr>");
    }
    if (data.status === 'online') {
        var decorated = ($.inArray(data.mac, macs) == -1 ? '' : ' (<strong>you!</strong>)');
        $("#tblDataFullStatus tbody").append(
            '<tr>' +
            '<td class="mac_entry">' + data.mac + decorated + "</td>" +
            '<td class="nick_entry">' + data.nick + "</td>" +
            '</tr>');
    }
};

function discardChanges(context) {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/tablemgr');
    // Just ask server resend the table
     socket.emit('uploadTable', {});
};

function editRow(context) {
    var $row = $(context).closest("tr");

    var id = $row.find(".id_entry");
    var mac = $row.find(".mac_entry");
    var nick = $row.find(".nick_entry");
    var buttonToolbox = $row.find(".buttonToolbox");
    // Store previous values for undo
    var prevNick = nick.text();
    var prevMac = mac.attr("data-mac");
    
    console.log(prevNick);
    mac.html("<input type='text' id='newmac' data-toggle='tooltip'" + 
             "data-placement='top' title='Use &quot ; &quot separator to add multiple MACs' value='" + 
             mac.attr("data-mac") + "'/>");
    nick.html("<input type='text' id='newnick' value='" + nick.text() + "'/>");

    // Change buttons to "Save" and "Apply"
    buttonToolbox.html(DISCARD_APPLY_BUTTON_GROUP);
};

function applyChanges(context) {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/tablemgr');
    var $row = $(context).closest("tr");
    var id = $row.find(".id_entry").text();
    var mac = $row.find(".mac_entry");
    var nick = $row.find(".nick_entry");
    var buttonToolbox = $row.find(".buttonToolbox");

    var newMacValue = document.getElementById("newmac").value;
    var newNickValue = document.getElementById("newnick").value;

    // Convert all symbols to upper, just to convenience
    newMacValue = newMacValue.toUpperCase();
    
    mac.html(newMacValue);
    nick.html(newNickValue);

    buttonToolbox.html(DELETE_EDIT_BUTTON_GROUP);
    
    socket.emit('edituser', {
        id: id,
        mac: newMacValue,
        nick: newNickValue,
    }); 
};

function deleteRow(context) {
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/tablemgr');
    var $row = $(context).closest("tr");
    var id = $row.find(".id_entry").text();

    socket.emit('deleteuser', {
        id: id,
    });    
};

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
