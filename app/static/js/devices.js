// Global: Device ID, which is pending for update
let deviceIDForUpdate = null;
let deviceTypeForUpdate = null;
function flashFirmware() {
  console.log("Flashing device: ", deviceIDForUpdate, deviceTypeForUpdate);
  const socket = new WebSocket("ws://" + location.host + "/reader_flasher");
  const logContainer = document.getElementById("log-container");

  let progress = 0;

  socket.addEventListener("open", () => {
    console.log(
      "WebSocket connection established, send device id for flashing",
    );
    socket.send(JSON.stringify({"device_id":deviceIDForUpdate, "device_type": deviceTypeForUpdate}));
  });
  function log(data) {
    const obj = JSON.parse(data);
    logContainer.innerHTML += `<span>${obj.text}</span><br>`;

    // Update progress bar
    document.querySelector(".progress-bar").style.width = `${obj.progress}%`;
    document.getElementById("statusText").innerText = `${obj.status}`;
  }

  function toggleLog() {
    logContainer.style.display =
      logContainer.style.display === "block" ? "none" : "block";
  }

  socket.addEventListener("message", (ev) => {
    log(ev.data);
  });
}

fetch("/api/devices")
  .then((response) => response.json())
  .then((data) => generateAccordionItems(data))
  .catch((error) => console.error("Error fetching data:", error));

function generateAccordionItems(devices) {
  const accordionItemsHTML = [];
  for (const device of devices) {
    const accordionItemHTML = `
      <div class="accordion-item">
        <h2 class="accordion-header">
          <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#flush-collapse-${device.id}" aria-expanded="false" aria-controls="flush-collapse-${device.id}">
            <p class="editable-field"><i class="bi bi-phone-vibrate-fill"></i> | <span class="deviceName" contenteditable="plaintext-only" id="device-${device.id}" onclick="makeEditable(event, '${device.id}')">${device.name}</span>
            <i class="bi bi-pencil-fill edit" onclick="makeEditable(event, '${device.id}', true)"></i></p>
          </button>
        </h2>

        <div id="flush-collapse-${device.id}" class="accordion-collapse collapse" data-bs-parent="#accordionFlushExample">
          <div class="accordion-body">
            <div class="d-flex justify-content-between align-items-center row">

              <div class="me-3 pb-3">
                Device id: ${device.id}, Device type: ${device.type}
              </div>

              <div>
                <button type="button" class="btn btn-primary me-3 col-12 col-sm-auto mb-1" data-bs-toggle="modal" data-bs-target="#flashDeviceModal" onclick="deviceIDForUpdate='${device.id}';deviceTypeForUpdate='${device.type}'">Flash Connected Device</button>
                <button type="button" class="btn btn-danger col-12 col-sm-auto mb-1" onclick="removeDevice('${device.id}')">Remove Device</button>
              </div>

            </div>
          </div>
        </div>
      </div>
            `;
    accordionItemsHTML.push(accordionItemHTML);
  }
  const devicesListElement = document.getElementById("devicesList");
  devicesListElement.innerHTML = accordionItemsHTML.join("");
}

function generateUUID() {
  var d = new Date().getTime()
  if (window.performance && typeof window.performance.now === "function") {
    d += window.performance.now() //use high-precision timer if available
  }
  var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = (d + Math.random() * 16) % 16 | 0
    d = Math.floor(d / 16)
    return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16)
  })
  return uuid
}

function addDevice(deviceName, isDeviceTool) {
  // Generate random UUID for device ID
  const deviceId = generateUUID();
  // Prepare device data
  const deviceData = {
    device_name: deviceName,
    device_id: deviceId,
    // Looks like there is a bug in bootstrap toogle 5, can not just get value of toggle:(
    device_type: (isDeviceTool ? "tool" : "door"),
  };
  // Make API call to add device
  fetch("/api/devices", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(deviceData),
  })
    .then((response) => {
      // Check if response status code is 201 (Created)
      if (response.status === 201) {
        alert("Device added successfully!");
        refreshDevicesList();
      } else {
        alert("Error adding device. Please try again later.");
      }
    })
    .catch((error) => {
      console.error("Error adding device:", error);
      alert("Error adding device. Please try again later.");
    });
}

function updateDevice(deviceId, deviceName) {
  console.log("updateDevice", deviceId, deviceName);
  // Prepare device data
  const deviceData = {
    name: deviceName,
  };
  // Make API call to update device
  fetch(`/api/devices/${deviceId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(deviceData),
  })
    .then((response) => {
      // Check if response status code is 200 (OK)
      if (response.status === 200) {
        alert("Device updated successfully!");
        refreshDevicesList();
      } else {
        alert("Error updating device. Please try again later.");
      }
    })
    .catch((error) => {
      console.error("Error updating device:", error);
      alert("Error updating device. Please try again later.");
    });
}

function removeDevice(deviceId) {
  fetch(`/api/devices/${deviceId}`, {
    method: "DELETE",
  })
    .then((response) => {
      if (response.status === 200) {
        alert("Device removed successfully!");
        refreshDevicesList();
      } else {
        alert("Error removing device. Please try again later.");
      }
    })
    .catch((error) => {
      console.error("Error removing device:", error);
      alert("Error removing device. Please try again later.");
    });
}

function refreshDevicesList() {
  fetch("/api/devices")
    .then((response) => response.json())
    .then((data) => generateAccordionItems(data))
    .catch((error) => console.error("Error fetching data:", error));
}

function makeEditable(event, deviceId, isEditIconClicked = false) {
  const element = document.getElementById(`device-${deviceId}`);
  if (isEditIconClicked) {
    element === document.activeElement ? element.blur() : element.focus();
  }
  let originalContent = element.textContent;

  element.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      this.blur();
    }
  });

  element.onblur = async function () {
    if (element.textContent === "" || element.textContent === originalContent) {
      // if the new name is empty, revert to the original name
      // TODO: add validation
      return;
    }
    await updateDevice(deviceId, element.textContent);
  };
}
