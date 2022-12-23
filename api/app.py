import time
from datetime import datetime as dt
import os
import re
from datetime import datetime as dt
from flask import Flask,  request, jsonify
from flask_restful import Api
from flask_cors import CORS
from threading import Thread
from subprocess import Popen, PIPE
from dotenv import load_dotenv
load_dotenv()

DEVELOPMENT = False
INIT_CALIBRATION_SECONDS = 20
CALIBRATION_STARTED = False
CALIBRATION_DONE = False
start_time = dt.now()
HOST_IP = os.getenv("HOST_IP")
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'sound')
sound_sensors = [f"{i}" for i in range(1, 17)]
FFMPEG_OUT = open("/tmp/ffmpeg_out", 'a+')
FFMPEG_ERR = open("/tmp/ffmpeg_err", 'a+')


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


playlist = find_audio_files()


def get_artist_by_time(now) -> str:
    for h in range(11, 21, 2):
        if now.hour < h and now.minute < 30:
            return "1"
        if now.hour < h and now.minute >= 30:
            return "2"
        if now.hour < h + 1 and now.minute < 30:
            return "3"
        if now.hour < h + 1 and now.minute >= 30:
            return "4"
    return "4"


# times = [
#     dt(2022, 1, 1, 10, 0),
#     dt(2022, 1, 1, 10, 30),
#     dt(2022, 1, 1, 11, 0),
#     dt(2022, 1, 1, 11, 30),
# ]
# for t in times:
#     print(get_artist_by_time(t))

class ExhibitArea:
    def __init__(self, id, approx_floor_height=240):
        self.sound_id = id
        # self.motion_id = id
        self.person_detected = False
        self.proc = None
        self.floor_ranges = []
        self.calibrate_range(approx_floor_height)
        self.last_range = approx_floor_height

    def calibrate_range(self, floor_range_reading):
        self.floor_ranges.append(floor_range_reading)
        self.floor_ranges = sorted(self.floor_ranges)
        self.trigger_range = self.floor_ranges[len(
            self.floor_ranges) // 2] - 20

    def set_person_detected(self, person_detected):
        self.person_detected = person_detected
        if self.person_detected == False and self.proc:
            self.proc.terminate()

    def play_audio(self):
        global playlist

        artist = get_artist_by_time(dt.now())
        channel = int(self.sound_id) - 1
        audio_file = playlist[artist][channel]

        while self.person_detected:
            with open('/tmp/play_audio.log', 'a+') as audio_log:

                cmd = f'ffmpeg -i {audio_file} -ac 16 -filter_complex "[0:a]pan=16c|c{channel}=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -'

                audio_log.write(f"{dt.now()}\n{cmd}\n" + ("-"*80) + '\n')

                self.proc = Popen(
                    cmd, shell=True, stdout=FFMPEG_OUT, stderr=FFMPEG_ERR)
                self.proc.wait()


area_map = {f"{sound_id}": ExhibitArea(sound_id) for sound_id in sound_sensors}
area_thread_map = {f"{sound_id}": Thread(
    target=area_map[sound_id].play_audio) for sound_id in sound_sensors}


# -------------------------------- FLASK API --------------------------------

app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route('/')
def index():
    return "Hello World"


@app.route('/data', methods=['GET'])
def data():
    # read data from encoded url
    global CALIBRATION_DONE, INIT_CALIBRATION_SECONDS, start_time, CALIBRATION_STARTED

    origin = request.remote_addr

    if not CALIBRATION_STARTED:
        start_time = dt.now()
        CALIBRATION_STARTED = True

    if DEVELOPMENT:
        CALIBRATION_DONE = True
        if origin != f"{HOST_IP}":
            return jsonify({"status": "development"})

    with open('/tmp/arduino_worker.log', 'a+') as log:
        res = ""

        try:
            # sensorID_ = request.get_json(force=True)['sensorID']
            # range_ = request.get_json(force=True)['range']
            sensorID_ = request.args.get('sensorID')
            range_ = int(request.args.get('range'))
            motion_ = int(request.args.get('motion'))

            area = area_map[sensorID_]
            thread = area_thread_map[sensorID_]

            if CALIBRATION_DONE:
                if range_ > 0 and range_ <= area.trigger_range:  # received valid range reading
                    # 5cm consistency check, additional filter
                    if DEVELOPMENT:
                        if not area.person_detected and not thread.is_alive():
                            area.set_person_detected(True)
                            thread.start()
                    elif abs(range_ - area.last_range) < 5:
                        if not area.person_detected and not thread.is_alive():
                            area.set_person_detected(True)
                            thread.start()
                    area.last_range = range_
                elif motion_ == 1:  # received valid motion reading
                    if not area.person_detected and not thread.is_alive():
                        area.set_person_detected(True)
                        thread.start()
                else:
                    area.set_person_detected(False)
                    area_thread_map[sensorID_] = Thread(
                        target=area_map[sensorID_].play_audio)
            else:
                area.calibrate_range(range_)
                if (dt.now() - start_time).seconds > INIT_CALIBRATION_SECONDS:
                    CALIBRATION_DONE = True

            res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {CALIBRATION_DONE}"
            print(f"{dt.now()} | {res}")
            log.write(f"{dt.now()} | {res}")
            return jsonify({"status": "ok"})
        except Exception as e:
            print(e)
            log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


if __name__ == '__main__':
    app.run(debug=True, host=f'{HOST_IP}', port=5000)
