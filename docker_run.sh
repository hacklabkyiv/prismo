#!/bin/bash

export HOST_HOSTNAME=$(hostnamectl hostname)
export HOST_WIFI_SSID=$(nmcli -s device wifi show-password | grep "SSID"| cut -d" " -f2)
export HOST_WIFI_PASSWORD=$(nmcli -s device wifi show-password | grep "Password"| cut -d" " -f2)

docker compose up
