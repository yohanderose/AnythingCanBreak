#!/bin/bash
pkill python
pkill ffmpeg
sleep 10 # wait for wlan connection
/Users/anythingcanbreak/.miniconda3/envs/web2/bin/python /Users/anythingcanbreak/Documents/sirikit_exhibit_final/api/app.py
