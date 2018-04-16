#!/bin/bash

set -e
set -x

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root"
  exit 1
fi

apt update && apt install -y python-gpiozero

ln -sf $(pwd)/button-machine.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable button-machine
systemctl restart button-machine
