#!/bin/bash
# ensure nothing we need is zombie
pkill python &
pkill ffmpeg &
sleep 120 # wait for wlan connection, and arduinos a) connect to wlan b) hit the host and c) and start posting
/Users/anythingcanbreak/.miniconda3/envs/web2/bin/python /Users/anythingcanbreak/sirikit_exhibit_final/api/app.py
