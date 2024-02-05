#!/bin/bash

export HOST_HOSTNAME=$(hostnamectl hostname)

docker compose up
