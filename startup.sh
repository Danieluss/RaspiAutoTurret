#!/bin/bash

cd $(dirname "$0")
sudo pigpiod
workon cv
python3 /home/pi/Desktop/turret.py
