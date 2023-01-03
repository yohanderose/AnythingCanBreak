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

import numpy as np
import cv2

from dotenv import load_dotenv
load_dotenv()

DEVELOPMENT = False
INIT_CALIBRATION_SECONDS = 10
HOST_IP = os.getenv("HOST_IP")
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'sound')
sound_sensors = [i for i in range(1, 17)]

num_imgs = len(sound_sensors)
arangement = (4, 4)
IMG_WIDTH = 320
IMG_HEIGHT = 240

default_id_img = np.zeros(
    (IMG_HEIGHT * arangement[1], IMG_WIDTH * arangement[0]))
print(
    f"Stacked grid of image dimension {default_id_img.shape} \n-- {num_imgs} arranged {arangement} ")

state_dict = dict(zip(sound_sensors, [False] * len(sound_sensors)))


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


def assign_exhibit_IPs():
    cmd = f"nmap -sn {HOST_IP[:-1]}0/24 -oG -" + \
        " | grep 'Status: Up' | awk '{print $2}' "
    # print(cmd)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8").split('\n')
    if len(err) > 0:
        print(err)
        return
    for ip in out:
        if len(ip) > 0:
            try:
                id = ping_ip_for_id(ip)
                if id > 0:
                    area_obj_map[id].ip = ip
                    print(f"Assigned {ip} to ExhibitAreaV2 {id}")
                    area_obj_map[id].video_stream = cv2.VideoCapture(
                        'http://'+ip)

            except Exception as e:
                pass


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


def get_frames_from_devices():
    global area_state_img, area_obj_map
    assign_exhibit_IPs()

    while True:
        for area in area_obj_map.values():
            if area.ip is None:
                continue
            try:
                if area.video_stream:
                    ret, frame = area.video_stream.read()
                    if ret:
                        # frame = cv2.resize(frame, (IMG_WIDTH, IMG_HEIGHT))
                        write_slice_from_id(
                            area_state_img, area.sound_id, frame[:, :, 0])

            except Exception as e:
                print(e)


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
    global area_state_img, state_dict

    _state = dict(zip(sound_sensors, [False] * len(sound_sensors)))
    contours, _ = cv2.findContours(
        area_state_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    point_contours = np.vstack(contours).squeeze()

    for point in point_contours:
        id = get_areaID_by_coordinate(point[0], point[1])
        _state[id] = True

    if _state != state_dict:
        state_dict = _state
        # apply_state_to_system()


def generate_UI_frames():
    global area_state_img
    while True:
        frame = cv2.imencode('.jpg', area_state_img)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# write_slice_from_id(area_state_img, 1, data=200)
# print(ping_ip_for_id('172.20.10.2'))
# get_frames_from_devices()
# assign_exhibit_IPs()
cv_consumer = Thread(target=get_frames_from_devices)
cv_detector = Thread(target=detect_update_state)
cv_consumer.start()
cv_detector.start()


def handle_sigkill(signum, frame):
    print("SIGKILL")
    for area in area_obj_map.values():
        if area.video_stream is not None:
            print(f"Releasing video stream {area.sound_id}")
            area.video_stream.release()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_sigkill)

# time.sleep(10)
# area_state_img = example_blobs.copy()
# example_blobs = np.array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 100., 100., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 100., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 200., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 200., 200., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 255., 255., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
#                           [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]], np.uint8)


# # # -------------------------------- FLASK API --------------------------------

app = Flask(__name__)
CORS(app)


@ app.route('/')
def index():
    return "Hello World"


@ app.route('/visual')
def visualise():
    return Response(generate_UI_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# @ app.route('/data', methods=['GET'])
# def data():
#     origin = request.remote_addr
#     res = ""

#     try:
#         # sensorID_ = request.get_json(force=True)['sensorID']
#         # range_ = request.get_json(force=True)['range']
#         sensorID_ = request.args.get('sensorID')
#         img_data = request.args.get('imgData')

#         write_slice_from_id(area_state_img, int(sensorID_), data=img_data)

#         res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
#         print(f"{dt.now()} | {res}")
#         log.write(f"{dt.now()} | {res}")
#         return jsonify({"status": "ok"})
#     except Exception as e:
#         print(e)
#         log.write(f"{dt.now()} | {origin} Error: {e}\n")

#     # return error response
#     return jsonify({"status": "error"})


app.run(debug=True, host=f'{HOST_IP}', port=5000)
