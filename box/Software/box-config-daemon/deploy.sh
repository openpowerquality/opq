#!/usr/bin/env bash

SERVICE="box-config-daemon.service"

sudo systemctl stop ${SERVICE}
sudo systemctl disable ${SERVICE}
sudo rm -rf /usr/local/box-config-daemon/*
sudo cp -R * /usr/local/box-config-daemon/.
sudo cp ${SERVICE} /etc/systemd/system/.
sudo systemctl enable ${SERVICE}
sudo systemctl start ${SERVICE}