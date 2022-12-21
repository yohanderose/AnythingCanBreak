# Simple flask API to read arduino serial data
# and send it to the client
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

DEVELOPMENT = True
INIT_CALIBRATION_SECONDS = 20
CALIBRATION_STARTED = False
CALIBRATION_DONE = False
start_time = dt.now()
HOST_IP = os.getenv("HOST_IP")
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'sounds')
sound_sensors = [f"{i}" for i in range(1, 17)]
FFMPEG_OUT = open("/tmp/ffmpeg_out", 'a+')
FFMPEG_ERR = open("/tmp/ffmpeg_err", 'a+')


def find_audio_file(id) -> str:
    files = os.listdir(SOUNDS_DIR)
    for file in files:
        if re.match(f"SPEAKER{id}_.*", file):
            return os.path.join(SOUNDS_DIR, file)

    return "file not found"


class ExhibitArea:
    def __init__(self, id, approx_floor_height=240):
        self.sound_id = id
        # self.motion_id = id
        self.person_detected = False
        self.audio_file = find_audio_file(id)
        self.proc = None
        self.calibrate_range(approx_floor_height)
        self.last_range = approx_floor_height

    def calibrate_range(self, floor_range_reading):
        self.floor_range = floor_range_reading
        self.trigger_range = floor_range_reading - 60

    def set_person_detected(self, person_detected):
        self.person_detected = person_detected
        if self.person_detected == False and self.proc:
            self.proc.terminate()

    def play_audio(self):
        while self.person_detected:
            cmd = f'ffmpeg -i {self.audio_file} -ac 16 -filter_complex "[0:a]pan=16c|c{int(self.sound_id) -1}=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -'
            self.proc = Popen(
                cmd, shell=True, stdout=FFMPEG_OUT, stderr=FFMPEG_ERR)
            self.proc.wait()


area_map = {f"{sound_id}": ExhibitArea(sound_id) for sound_id in sound_sensors}
area_thread_map = {f"{sound_id}": Thread(
    target=area_map[sound_id].play_audio) for sound_id in sound_sensors}

# area_map["1"].set_person_detected(True)
# t = area_thread_map["1"]
# t.start()

# time.sleep(2)
# if t.is_alive():
#     area_map["1"].set_person_detected(False)
#     t.join()


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
                    if abs(range_ - area.last_range) < 5:
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
