#!/bin/bash
pkill python
pkill ffmpeg
sleep 60 # wait for wlan connection and arduinos to start posting
/Users/anythingcanbreak/.miniconda3/envs/web2/bin/python /Users/anythingcanbreak/Documents/sirikit_exhibit_final/api/app.py
