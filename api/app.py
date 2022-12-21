# Simple flask API to read arduino serial data
# and send it to the client
import time
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


def find_audio_file(id) -> str:
    files = os.listdir(SOUNDS_DIR)
    for file in files:
        if re.match(f"SPEAKER{id}_.*", file):
            return os.path.join(SOUNDS_DIR, file)

    return "file not found"


HOST_IP = os.getenv("HOST_IP")
SOUNDS_DIR = "./api/sounds"
sound_sensors = [f"{i}" for i in range(1, 17)]


class ExhibitArea:
    def __init__(self, id):
        self.sound_id = id
        # self.motion_id = id
        self.person_detected = False
        self.audio_file = find_audio_file(id)
        self.proc = None

    def set_person_detected(self, person_detected):
        self.person_detected = person_detected
        if self.person_detected == False and self.proc:
            self.proc.wait()
            self.proc.terminate()
            self.proc = None

    def play_audio(self):
        while self.person_detected:
            cmd = f'ffmpeg -i {self.audio_file} -ac 16 -filter_complex "[0:a]pan=16c|c{int(self.sound_id) -1}=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -'
            self.proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
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

    with open('/tmp/arduino_worker.log', 'a+') as log:
        res = ""
        origin = request.remote_addr
        try:
            # sensorID_ = request.get_json(force=True)['sensorID']
            # range_ = request.get_json(force=True)['range']
            sensorID_ = request.args.get('sensorID')
            range_ = request.args.get('range')
            motion_ = request.args.get('motion')

            res = f"sensorID: {sensorID_}, range: {range_}, motion: {motion_}"
            log.write(f"{dt.now()} | ({origin}) {res}\n")
            print(f"{dt.now()} | ({origin}) {res}")
            area = area_map[sensorID_]
            thread = area_thread_map[sensorID_]

            if int(motion_) == 1:  # or/and range < floor distance - height
                if not area.person_detected and not thread.is_alive():
                    area.set_person_detected(True)
                    thread.start()
            else:
                area.set_person_detected(False)
                area_thread_map[sensorID_] = Thread(
                    target=area_map[sensorID_].play_audio)

            return jsonify({"status": "ok"})
        except Exception as e:
            print(e)
            log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


if __name__ == '__main__':
    app.run(debug=True, host=f'{HOST_IP}', port=5000)
