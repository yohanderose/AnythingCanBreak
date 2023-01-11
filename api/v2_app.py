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

from flask import Flask, appcontext_tearing_down,  request, jsonify, Response
from flask_cors import CORS
from threading import Thread
from subprocess import Popen, PIPE
from multiprocessing import Pool, Process
from concurrent.futures import ThreadPoolExecutor
import PySimpleGUI as sg

import matplotlib.pyplot as plt
import dash
from dash.dependencies import Output, Input
from dash import Dash, html, dcc
import plotly.express as px


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


def get_areaID_by_coordinate(x, y) -> int:
    global default_id_img
    # Safe constant time reads from combo data
    return default_id_img[x][y] + 1


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
                    break
    except Exception as e:
        # allow other random devices to be pinged without crashing
        pass


def assign_exhibitarea_IPs():
    global online_set

    while True:
        host_ip = ".".join(HOST_IP.split(".")[:-1])
        cmd = f"nmap -sn --system-dns {host_ip}.0/24 -oG -" + \
            " | grep 'Status: Up' | awk '{print $2}' "
        # print(cmd)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        out = out.decode("utf-8").split('\n')
        if len(err) > 0:
            print(err)
        with ThreadPoolExecutor(max_workers=32) as executor:
            executor.map(_assign_exhibitarea_IP, out)

        time.sleep(5)


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
png_area_img = cv2.imencode(
    '.png', area_state_img)[1].tobytes()


def write_frames_from_devices(area: ExhibitAreaV2):
    global png_area_img, online_set

    while True:
        if area.ip is not None:  # Device  detected
            # print(f'Area {area.sound_id}')
            try:
                if area.video_stream:
                    ret, frame = area.video_stream.read()
                    if ret:
                        # Crop to square and convert to greyscale
                        frame = frame[-IMG_HEIGHT:, -IMG_WIDTH:, 0]
                        # # Add Blur
                        # frame = cv2.GaussianBlur(frame, (5, 5), 0)
                        write_slice_from_id(
                            area_state_img, area.sound_id, frame)

                        png_area_img = cv2.imencode(
                            '.png', area_state_img)[1].tobytes()
                    else:
                        if area.video_stream:
                            area.video_stream.release()
                            area.video_stream = None
                            area.video_stream = cv2.VideoCapture(
                                'http://' + area.ip)
            except Exception as e:
                online_set.remove(area.sound_id)
                print(e)


sg.theme("DarkBrown1")
sg_ui_window = sg.Window('Exhibit Area Overview', [
    [sg.Image(data='', key='image')],
    [sg.Text("Online")],
    [sg.Text(f"{online_set}", key='online')],
    [sg.Text("Person detected")],
    [sg.Text(f"{state_dict}", key='states')]
], location=(800, 400))


def read_frames_from_devices():
    global area_state_img, area_obj_map, sg_ui_window, state_dict

    reader_threads = [Thread(target=assign_exhibitarea_IPs)] + [Thread(
        target=write_frames_from_devices, args=(area,)) for area in area_obj_map.values()]

    for t in reader_threads:
        t.start()

    while True:
        sg_ui_window.read(timeout=10)
        sg_ui_window['image'].update(png_area_img)
        sg_ui_window['states'].update(value=f"{state_dict}")
        sg_ui_window['online'].update(value=f"{online_set}")


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


def detect_update_state():
    global area_state_img, state_dict, area_obj_map

    brightness = 30
    contrast = 2

    while True:
        try:
            _state = dict(zip(sound_sensors, [False] * len(sound_sensors)))
            contours, _ = cv2.findContours(
                area_state_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            point_contours = np.vstack(contours).squeeze()

            for point in point_contours:
                id = get_areaID_by_coordinate(point[0], point[1])
                if area_obj_map[id].video_stream:
                    _state[id] = True

            if _state != state_dict:
                state_dict = _state
                # apply_state_to_system()
        except Exception as e:
            # print("OPENCV ERROR DETECTING CONTOURS -- ", e)
            pass


def handle_sigkill(signum, frame):
    print("SIGKILL")

    for area in area_obj_map.values():
        if area.video_stream is not None:
            print(f"Releasing video stream {area.sound_id}")
            area.video_stream.release()
    cv2.destroyAllWindows()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_sigkill)


def generate_UI_frames():
    global area_state_img
    ui_frame = cv2.imencode('.jpg', area_state_img)[1].tobytes()

    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + ui_frame + b'\r\n')
        ui_frame = cv2.imencode('.jpg', area_state_img)[1].tobytes()

# # # -------------------------------- API --------------------------------


# app = Dash(__name__)


# @app.callback(
#     Output('live-graph', 'children'),
#     [Input('graph-update', 'n_intervals')]
# )
# def display_area_overview(n):
#     global area_state_img

#     fig = px.imshow(area_state_img, color_continuous_scale="gray")
#     fig.update_layout(coloraxis_showscale=False)
#     fig.update_xaxes(showticklabels=False)
#     fig.update_yaxes(showticklabels=False)

#     return dcc.Graph(figure=fig)


# app.layout = html.Div([
#     html.H1("Exhibit Overview"),

#     html.Div(
#         [
#             html.Div(id='live-graph'),
#             dcc.Interval(
#                 id='graph-update',
#                 interval=100,
#                 n_intervals=0
#             ),
#         ]
#     )
# ])

# app.run(debug=True, host=f'{HOST_IP}', port=5000)


# write_slice_from_id(area_state_img, 1, data=200)
# print(ping_ip_for_id('172.20.10.2'))
# print(ping_ip_for_id('172.20.10.4'))
# read_frames_from_devices()
cv_consumer = Process(target=read_frames_from_devices)
cv_consumer.start()
cv_detector = Process(target=detect_update_state)
cv_detector.start()
