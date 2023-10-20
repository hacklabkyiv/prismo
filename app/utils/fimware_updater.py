#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reader firmware update tool. It erases memory, flashes Micropython and 
working scripts itself to connected device.

@author: Artem Synytsyn <a.synytsyn@gmail.com>
"""
from flask import Flask, render_template
from flask_sock import Sock
import subprocess
import shlex
import pathlib

# TODO: Read all these pathes from config file
ESPTOOL_PATH = "/home/artsin/Dev/esptool/esptool.py"
AMPY_PATH = "/home/artsin/.local/bin/ampy"
MICROPYTHON_DISTRO_PATH = "/home/artsin/Downloads/ESP32_GENERIC-20231005-v1.21.0.bin"

READER_FW_PATH = "/home/artsin/Dev/prismo-reader/src/"

command_erase = ["python3", ESPTOOL_PATH, "erase_flash"]
command_flash_micropython = [
    "python3",
    ESPTOOL_PATH,
    "--baud",
    "460800",
    "write_flash",
    "-z",
    "0x1000",
    MICROPYTHON_DISTRO_PATH,
]
# TODO: Serial port autodetect
commands_upload_scripts = [AMPY_PATH, "-p", "/dev/ttyUSB0", "put"]


def erase_flash(socket):
    process = subprocess.Popen(command_erase, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            data = output.strip()
            print(data)
            socket.send(str(data))
            if b"Hard resetting via RTS pin" in data:
                return True
    return False


def flash_micropython_binary(socket):
    process = subprocess.Popen(command_flash_micropython, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            data = output.strip()
            print(data)
            socket.send(str(data))
            if b"Hard resetting via RTS pin" in data:
                return True
    return False


def upload_python_scripts(socket):
    firmware_files = [f for f in pathlib.Path(READER_FW_PATH).iterdir() if f.is_file()]
    for file in firmware_files:
        socket.send("Download: " + str(file.name))
        # Make a copy, since we do not want to change original command template
        command = commands_upload_scripts[:]
        command.append(str(file))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        process.wait()
        socket.send("OK")
    return True


def update_firmware_full(socket):
    socket.send("--------- FLASH ERASE ----------------")
    result = erase_flash(socket)
    print("Erase flash result: ", result)
    socket.send("------- MICROPYTHON INSTALL ----------")
    result = flash_micropython_binary(socket)
    print("upload script")
    socket.send("----------- UPLOAD FIRMWARE ----------")
    upload_python_scripts(socket)
    socket.send("----------- DONE! ----------")
