#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID Reader firmware management module
"""
import json
import re
import subprocess
import uuid
import os
from pathlib import Path

from flask import current_app as app


def update_firmware_full(socket, device_id, device_type):
    """Run full firmware update, by running firmware updater script

    This function runs firmware updater script, which erases memory, flashes
    Micropython and working scripts to connected device.

    It sends data to frontend, which is used for showing progress of firmware
    update.

    Arguments:
    socket -- communication websocket
    device_id -- device ID string, MUST be UUID string in format
                                        550e8400-e29b-41d4-a716-446655440000
    device_type -- type of device, should be "tool" or "door"

    Returns:
    bool -- True if firmware update was successful, False otherwise
    """
    # pylint: disable=broad-exception-caught
    app.logger.info("Updating firmware for device %s", device_id)
    # Data used for transfer to frontend
    data = {"text": "", "progress": 0, "status": "is_running"}
    try:
        script_path = Path(app.config["PRISMO"]["READER_FIRMWARE_FLASHING_SCRIPT_PATH"])
        # Check and set wifi credentials as environment variables. Since flasher script requires
        # them as ENV variables,and looks like Raspberry Pi OS do not allows to get wifi password
        # to console, this trick is used here.
        run_environment = os.environ.copy()
        run_environment["HOST_WIFI_SSID"] = app.config["PRISMO"]["WIFI_SSID"]
        run_environment["HOST_WIFI_PASSWORD"] = app.config["PRISMO"]["WIFI_PASSWORD"]
        script_cwd = script_path.parent
        process = subprocess.Popen([script_path, device_id, device_type], cwd=script_cwd,

                                   stdout=subprocess.PIPE, env=run_environment)
    except FileNotFoundError:
        data["text"] = "Cannot find firmware update script"
        data["status"] = "Device flashing failed"
        socket.send(json.dumps(data))
        app.logger.error("Cannot find firmware update script")
        return False
    except Exception as e:
        data["text"] = "Exception %s during running flashing script"
        data["status"] = "Device flashing failed"
        socket.send(json.dumps(data))
        app.logger.error("Exception during running flashing script: %s", e)
        return False
    # TODO: add process timeout, to exit from socket if process is too long # pylint: disable=fixme
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            text = output.strip()
            app.logger.info("%s", text.decode("utf-8"))
            data["text"] = text.decode("utf-8")
            # Get progress value
            progress_match = re.search(r"PROGRESS:\d+", data["text"])
            if progress_match:
                data["progress"] = int(progress_match.group(0).split(":")[1])

            status_match = re.search(r"STATUS:(.*)]", data["text"])
            if status_match:
                data["status"] = status_match.group(1).strip()
                app.logger.info("Flashing, status updated: %s", data["status"])
            socket.send(json.dumps(data))

            failed_match = re.search(r"FAILED]", data["text"])
            if failed_match:
                app.logger.info("Flashing, status failed found, returning: %s", data["status"])
                return False

    return True


def firmware_updater_route(websocket):
    device_id = None
    device_type = None
    while device_id is None:
        message = websocket.receive()
        if message:
            try:
                json_data = json.loads(message)
                # Check if we have received valid uuid string.
                uuid.UUID(json_data["device_id"])
                device_id = json_data["device_id"]
                device_type = json_data["device_type"]

            except ValueError:
                app.logger.error("Wrong message received: %s", message)

    if device_id is not None and device_type is not None:
        update_result = update_firmware_full(websocket, device_id, device_type)
        app.logger.warning("Update result: %s", update_result)
    else:
        app.logger.warning("No device id or device type was received")
    app.logger.warning("Close websocket")
