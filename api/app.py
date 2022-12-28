from exhibit import ExhibitArea
import time
from datetime import datetime as dt
import os
import re
from datetime import datetime as dt
from flask import Flask, appcontext_tearing_down,  request, jsonify
from flask_restful import Api
from flask_cors import CORS
from threading import Thread
from subprocess import Popen, PIPE
from dotenv import load_dotenv
load_dotenv()

DEVELOPMENT = False
INIT_CALIBRATION_SECONDS = 10
HOST_IP = os.getenv("HOST_IP")
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), 'sound')
sound_sensors = [f"{i}" for i in range(1, 17)]


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
log = open('/tmp/arduino_worker.log', 'a+')

area_map = {f"{sound_id}": ExhibitArea(
    sound_id, playlist) for sound_id in sound_sensors}
area_thread_map = {f"{sound_id}": Thread(
    target=area_map[sound_id].play_audio) for sound_id in sound_sensors}


def process(area, thread, range_):
    if not area.calbration_started:
        area.calibration_started = True
        area.start_time = dt.now()

    if area.calibration_finished:
        if range_ > 0 and range_ <= area.trigger_range:
            if not area.person_detected and not thread.is_alive():
                area.set_person_detected(True)
                thread.start()
            # 5cm consistency check first -> abs(range_ - area.last_range) < 5
        # elif motion_ == 1:  # received valid motion reading
        #     if not area.person_detected and not thread.is_alive():
        #         area.set_person_detected(True)
        #         thread.start()
        elif abs(range_ - area.floor_range) < 5:
            if area.person_detected:
                area.set_person_detected(False)
                area_thread_map[area.sensorID] = Thread(
                    target=area_map[area.sensorID].play_audio)
    else:
        area.calibrate_range(range_)
        if (dt.now() - area.start_time).seconds > INIT_CALIBRATION_SECONDS:
            area.calibration_finished = True
            area.set_person_detected(False)
            area_thread_map[area.sensorID] = Thread(
                target=area_map[area.sensorID].play_audio)


# t = area_thread_map["1"]
# area_map["1"].person_detected = True
# t.start()
# if t.is_alive():
#     t.join()

# -------------------------------- FLASK API --------------------------------

app = Flask(__name__)
api = Api(app)
CORS(app)


@ app.route('/')
def index():
    return "Hello World"


@ app.route('/data', methods=['GET'])
def data():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/1', methods=['GET'])
def data1():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/2', methods=['GET'])
def data2():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/3', methods=['GET'])
def data3():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/4', methods=['GET'])
def data4():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/5', methods=['GET'])
def data5():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/6', methods=['GET'])
def data6():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/7', methods=['GET'])
def data7():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/8', methods=['GET'])
def data8():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/9', methods=['GET'])
def data9():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/10', methods=['GET'])
def data10():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/11', methods=['GET'])
def data11():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/12', methods=['GET'])
def data12():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/13', methods=['GET'])
def data13():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/14', methods=['GET'])
def data14():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/15', methods=['GET'])
def data15():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
        print(f"{dt.now()} | {res}")
        log.write(f"{dt.now()} | {res}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(e)
        log.write(f"{dt.now()} | {origin} Error: {e}\n")

    # return error response
    return jsonify({"status": "error"})


@ app.route('/16', methods=['GET'])
def data16():
    origin = request.remote_addr
    res = ""

    try:
        # sensorID_ = request.get_json(force=True)['sensorID']
        # range_ = request.get_json(force=True)['range']
        sensorID_ = request.args.get('sensorID')
        range_ = int(request.args.get('range'))
        motion_ = int(request.args.get('motion'))

        area = area_map[sensorID_]
        thread = area_thread_map[sensorID_]

        process(area, thread, range_)

        res = f"({origin}) sensorID: {sensorID_}, range: {range_}, trigger_range {area.trigger_range}, motion: {motion_}, calibrated: {area.calibration_finished}"
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
