# RaspiAutoTurret

Pan-tilt surveillance camera project for raspberry pi 4 with object detection.

## Requirements
- 2x servo for pan and tilt of your camera
- pan-tilt servo mount
- rasberry pi 4B (I didn't check backward compatibility, but the only thing I would be concerned about is hardware PWM, which servos desperately need)
- some raspi camera module

## Functionality
What it can do:
### Livestreaming
Check out your camera view at ${your-raspi-ip}:8080, once your raspi is connected via WiFi or some other network.

If there is a screen connected to your raspi and you use desktop OS version, you can specify `-R true` flag to see your windowed camera view.

### Object detection
Detect any object you provide `haarcascade_*.xml` file for.

### DB logging
Track your detection logs in mysqldb.

## Installation

- pull this repo to raspi
- configure python3 virtual environment with opencv 
https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/
- enable and plug in camera module 
https://thepihut.com/blogs/raspberry-pi-tutorials/16021420-how-to-install-use-the-raspberry-pi-camera
- download pigpio library
http://abyz.me.uk/rpi/pigpio/download.html
- configure mysqldb, if you'd like to log object detections in database (create turretdb there)
https://dev.mysql.com/doc/mysql-getting-started/en/
- connect your pan servo to GPIO 12 and tilt to GPIO 18 (default)
- connect your servos to a power supply - VCC/GND pins on raspi should suffice (at least it worked in my case, with raspi powered by 5.1V/3A)

## Usage
NOTE: you might have to update startup.sh with the name of your venv, in case you want to use it.

- make sure you have your pigpio service running, `pigpiod`
- if you followed the tutorial: `workon ${whatever_your_virtualenv_name_with_cv_is}`
if you didn't use virtualenvwrapper - change your venv to the one with cv some other way
- `python3 src/turret.py`

`turret.py` options:

usage: turret.py [-h] [-r RESOLUTION] [-F FRAMERATE] [-T ROTATION] [-R RENDER]
                 [-S STREAM] [--sr_port SR_PORT] [-C CLASSIFIERS]
                 [-D DATABASE] [--db_on DB_ON] [--db_host DB_HOST]
                 [--db_user DB_USER] [--db_password DB_PASSWORD]
                 [--db_cooldown DB_COOLDOWN]
                 

optional arguments:

  -h, --help            show this help message and exit
  
  -r RESOLUTION, --resolution RESOLUTION
                        camera resolution, usage: -R width,height
                        
  -F FRAMERATE, --framerate FRAMERATE
                        camera framerate
                        
  -T ROTATION, --rotation ROTATION
                        camera rotation
                        
  -R RENDER, --render RENDER
                        draw a window with turret vision
                        
  -S STREAM, --stream STREAM
                        host turret vision webapp
                        
  --sr_port SR_PORT     webapp port
  
  -C CLASSIFIERS, --classifiers CLASSIFIERS
                        list of opencv .xml cascade classifiers, usage: -C
                        /example/path,/example/path2
                        
  -D DATABASE, --database DATABASE
                        save detection history to database
                        
  --db_on DB_ON         use mysql db
  
  --db_host DB_HOST     mysql db host
  
  --db_user DB_USER     mysql db user
  
  --db_password DB_PASSWORD
                        mysql db password
                        
  --db_cooldown DB_COOLDOWN
                        detection db write cooldown
                        
