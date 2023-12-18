#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID Reader firmware management module
"""
import json
import re
import subprocess
import uuid
from pathlib import Path

from flask import current_app as app


def update_firmware_full(socket, device_id):
    """Run full firmware update, by running firmware updater script

    This function runs firmware updater script, which erases memory, flashes
    Micropython and working scripts to connected device.

    It sends data to frontend, which is used for showing progress of firmware
    update.

    Arguments:
    socket -- communication websocket
    device_id -- device ID string, MUST be UUID string in format
                                        550e8400-e29b-41d4-a716-446655440000

    Returns:
    bool -- True if firmware update was successful, False otherwise
    """
    # pylint: disable=broad-exception-caught
    app.logger.info("Updating firmware for device %s", device_id)
    # Data used for transfer to frontend
    data = {"text": "", "progress": 0, "status": "is_running"}
    try:
        script_path = Path(app.config["PRISMO"]["READER_FIRMWARE_FLASHING_SCRIPT_PATH"])
        script_cwd = script_path.parent
        process = subprocess.Popen([script_path, device_id], cwd=script_cwd, stdout=subprocess.PIPE)
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
    while device_id is None:
        message = websocket.receive()
        if message:
            try:
                # Check if we have received valid uuid string.
                uuid.UUID(message)
                device_id = message
            except ValueError:
                print("No uuid string was received:", message)

    if device_id is not None:
        update_result = update_firmware_full(websocket, device_id)
        app.logger.warning("Update result: %s", update_result)
    else:
        app.logger.warning("No device id was received")
    app.logger.warning("Close websocket")
