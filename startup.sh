#!/bin/bash

cd $(dirname "$0")
sudo pigpiod
sudo /home/pi/.virtualenvs/cv/bin/python3 /home/pi/Desktop/turret.py
