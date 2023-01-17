from PySimpleGUI.PySimpleGUI import subprocess
from dotenv import load_dotenv
import cv2
import numpy as np
import signal
import sys
from v2_exhibit import ExhibitAreaV2
import time
from datetime import datetime as dt
import os
import re
from datetime import datetime as dt
import requests
from datetime import datetime as dt

from flask import Flask, appcontext_tearing_down,  request, jsonify, Response
from flask_cors import CORS
from threading import Thread
from subprocess import Popen, PIPE, run
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import PySimpleGUI as sg

import matplotlib.pyplot as plt
import dash
from dash.dependencies import Output, Input
from dash import Dash, html, dcc
import plotly.express as px

"""
TODO
    server integration
        ✅ (test) obj detection unit testing / simulating esp -> taking sample images from one device and storing in ./tmp dir
        ✅ (bug) frame and ref_frame approximation (light/dust variation) -> applying blur to frames before assess difference
        ❎ (bug) gui very slow 
        ❎ (feat) connection maintainer (extending assignment)
        ❎ (docs) update readme and site machine
            - update system overview diagram
            - update start_here.sh.command
            - film clips for video

    esp32 edge cases
        ✅ (feat) wifi connection timeout
        ❎ (feat) wifi dropout -> reset
        ❎ (feat) camera issues -> reset
"""

load_dotenv()

HOST_IP = os.getenv("HOST_IP")
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'sound')
sound_sensors = [i for i in range(1, 17)]

num_imgs = len(sound_sensors)
arangement = (4, 4)
IMG_WIDTH = 240
IMG_HEIGHT = 240

default_id_img = np.zeros(
    (IMG_HEIGHT * arangement[1], IMG_WIDTH * arangement[0])).astype(np.uint8)
print(
    f"Stacked grid of image dimension {default_id_img.shape} \n-- {num_imgs} arranged {arangement} ")

state_dict = dict(zip(sound_sensors, [False] * len(sound_sensors)))
online_set = set()


def find_audio_files() -> dict:
    playlist = {}
    for artist in os.listdir(SOUNDS_DIR):
        files = os.listdir(os.path.join(SOUNDS_DIR, artist))
        songs = []
        for i in range(1, 17):
            for file in files:
                if file.startswith(f"speaker{i}."):
                    songs.append(os.path.join(SOUNDS_DIR, artist, file))

        playlist[artist] = songs

    return playlist


def write_slice_from_id(arr, id, data=1):
    # Concurrent safe write to shared combo-data array
    # WARNING -- updates in place
    print(f"Writing slice from id {id}")
    id = id - 1
    row = (id // arangement[0]) * IMG_WIDTH
    col = (id % arangement[1]) * IMG_HEIGHT
    arr[col:col+IMG_HEIGHT, row:row+IMG_WIDTH] = data


def read_slice_from_id(arr, id):
    id = id - 1
    row = (id // arangement[0]) * IMG_WIDTH
    col = (id % arangement[1]) * IMG_HEIGHT
    return arr[col:col+IMG_HEIGHT, row:row+IMG_WIDTH].copy()


# def get_areaID_by_coordinate(x, y) -> int:
#     global default_id_img
#     # Safe constant time reads from combo data
#     return default_id_img[x][y]


def ping_ip_for_id(ip) -> int:
    resp = requests.get(f"http://{ip}/id")
    if resp.status_code == 200:
        id = re.findall(r"\d+", resp.text)[0]
        return int(id)
    return -1


def _assign_exhibitarea_IP(ip):
    global area_obj_map, online_set

    try:
        id = ping_ip_for_id(ip)
        if id > 0 and id <= 16 and id not in online_set:
            print(f"Found device with id {id} at {ip}")
            online_set.add(id)
            while True:
                area_obj_map[id].ip = ip
                area_obj_map[id].video_stream = cv2.VideoCapture(
                    'http://'+ip)
                if area_obj_map[id].video_stream.isOpened():
                    print(f"Assigned {ip} to ExhibitAreaV2 {id}")
                    ret, frame = area_obj_map[id].video_stream.read()
                    if ret:
                        frame = frame[-IMG_HEIGHT:, -IMG_WIDTH:, 0]
                        area_obj_map[id].ref_frame = frame
                        break

    except Exception as e:
        # allow other random devices to be pinged without crashing
        pass


def manage_exhibitarea_IPs():
    host_ip = ".".join(HOST_IP.split(".")[:-1])
    cmd = f"nmap -sn --system-dns {host_ip}.0/24 -oG -" + \
        " | grep 'Status: Up' | awk '{print $2}' "
    # print(cmd)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8").split('\n')
    if len(err) > 0:
        print(err)
    for ip in out:
        _assign_exhibitarea_IP(ip)
    # with ThreadPoolExecutor(max_workers=12) as executor:
    #     executor.map(_assign_exhibitarea_IP, out)


playlist = find_audio_files()
log = open('/tmp/arduino_worker.log', 'a+')

area_obj_map = {sound_id: ExhibitAreaV2(
    sound_id, playlist) for sound_id in sound_sensors}
area_thread_map = {sound_id: Thread(
    target=area_obj_map[sound_id].play_audio) for sound_id in sound_sensors}

# Init placeholder greyscale image as starting state
for i in range(1, num_imgs+1):
    write_slice_from_id(default_id_img, i, data=i)
area_state_img = default_id_img.copy()


def write_frames_from_devices(area: ExhibitAreaV2, make_testdata=False):
    # make_testdata = True

    if make_testdata:
        subprocess.run(f'mkdir -p ./tmp/{area.sound_id}', shell=True)
    count = 0

    while True:
        if area.ip is not None:  # Device  detected
            # print(f'Area {area.sound_id}')
            try:
                if area.video_stream:
                    ret, frame = area.video_stream.read()
                    if ret:
                        # Crop to square and convert to greyscale
                        frame = frame[-IMG_HEIGHT:, -IMG_WIDTH:, 0]
                        # if area.ref_frame is None:
                        #     area.ref_frame = frame
                        #     continue

                        write_slice_from_id(
                            area_state_img, area.sound_id, frame)

                        if make_testdata:
                            file = f"./tmp/{area.sound_id}/{count}.png"
                            cv2.imwrite(
                                file, frame)
                            count += 1
                            print("writing ", file)
                            time.sleep(2.5)

                        # print(area.ref_frame.shape, frame.shape)
                        print(
                            f'Change detected in {area.sound_id}: ', detect_change(area.ref_frame, frame))
                    else:
                        if area.video_stream:
                            area.video_stream.release()
                            area.video_stream = None
                            area.video_stream = cv2.VideoCapture(
                                'http://' + area.ip)
            except Exception as e:
                print(e)


sg.theme("DarkBrown1")
sg_ui_window = sg.Window('Exhibit Area Overview', [
    [sg.Image(filename='', key='image')],
    [sg.Text("Online")],
    [sg.Text(f"{online_set}", key='online')],
    [sg.Text("Person detected")],
    [sg.Text(f"{state_dict}", key='states')]
], location=(800, 400))


def read_frames_from_devices():
    global area_state_img, area_obj_map, sg_ui_window, state_dict

    reader_threads = [Thread(
        target=write_frames_from_devices, args=(area,)) for area in area_obj_map.values()]

    for t in reader_threads:
        t.start()


def apply_state_to_system():
    global state_dict
    for id, state in state_dict.items():
        area = area_obj_map[id]
        thread = area_thread_map[id]
        if state:
            if not area.person_detected and not thread.is_alive():
                area.set_person_detected(True)
                thread.start()
        else:
            if area.person_detected and thread.is_alive():
                area.set_person_detected(False)
                area.set_person_detected(False)
                area_thread_map[area.sound_id] = Thread(
                    target=area_obj_map[area.sound_id].play_audio)


def detect_change(refFrame, curFrame):
    # Blur to reduce noise
    refFrame = cv2.GaussianBlur(refFrame, (9, 9), 0)
    curFrame = cv2.GaussianBlur(curFrame, (9, 9), 0)

    # Calculate the absolute difference between the images
    difference = cv2.absdiff(refFrame, curFrame)

    # Threshold the difference image
    _, difference = cv2.threshold(difference, .15, 1, cv2.THRESH_BINARY)
#     print(difference)

    # Dilate the difference image to amplify the changes
    kernel = np.ones((1, 1), np.uint8)
    difference = cv2.dilate(difference, kernel, iterations=3)

#     plt.imshow(difference, cmap='gray')
#     plt.show()
    return True if cv2.countNonZero(difference) > 0 else False


def process_frames_from_devices(area: ExhibitAreaV2):
    global online_set, state_dict, area_state_img

    if area.sound_id in online_set and area.video_stream and area.ref_frame:
        state_dict[area.sound_id] = detect_change(
            area.ref_frame, read_slice_from_id(area_state_img, id))

    print(state_dict[area.sound_id])


def detect_update_state():
    global state_dict, area_obj_map

    improc_threads = [Thread(
        target=process_frames_from_devices, args=(area,)) for area in area_obj_map.values()]
    for t in improc_threads:
        t.start()

    while True:
        # for area in area_obj_map.values():
        #     process_frames_from_devices(area)

        # print(dt.now(), [state_dict[1], state_dict[2]])
        # apply_state_to_system()
        time.sleep(.01)


def run_GUI():
    global sg_ui_window, area_state_img, state_dict, online_set
    while True:
        sg_ui_window.read(timeout=10)
        sg_ui_window['image'].update(data=cv2.imencode(
            '.png', area_state_img)[1].tobytes())
        sg_ui_window['states'].update(value=f"{state_dict}")
        sg_ui_window['online'].update(value=f"{online_set}")


def handle_sigkill(signum, frame):
    print("SIGKILL")

    for area in area_obj_map.values():
        if area.video_stream is not None:
            print(f"Releasing video stream {area.sound_id}")
            area.video_stream.release()
    sys.exit(0)


def start_component(proc):
    if proc == "gui":
        run_GUI()
    if proc == "networker":
        while True:
            manage_exhibitarea_IPs()
            time.sleep(5)
    if proc == "consumer":
        read_frames_from_devices()
    if proc == "processor":
        detect_update_state()


signal.signal(signal.SIGINT, handle_sigkill)
components = [
    'gui',
    'networker',
    'consumer',
    # 'processor'
]

with ThreadPoolExecutor(len(components)) as pool:
    pool.map(start_component, components)
