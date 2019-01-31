#!/usr/bin/env bash

sudo rm -rf /usr/local/box-config-daemon/*
sudo cp -R * /usr/local/box-config-daemon/.
sudo cp box-config-daemon.service /etc/systemd/system/.
sudo systemctl enable box-config-daemon.service