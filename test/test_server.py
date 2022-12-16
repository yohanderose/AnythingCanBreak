import time
import requests
from flask import jsonify

HOSTNAME = "http://172.20.10.5"
# HOSTNAME = "https://0a80-2001-44c8-4134-762-da69-323d-eb95-3fba.ngrok.io"
PORT = 5000


def test_server():
    r = None
    if HOSTNAME.startswith("https"):
        r = requests.get(HOSTNAME)
    else:
        r = requests.get(HOSTNAME + ":" + str(PORT))
    assert r.status_code == 200


def test_arduino_serial_output():
    r = None
    url = None
    if HOSTNAME.startswith("https"):
        url = f"{HOSTNAME}/data"
    else:
        url = f"{HOSTNAME + ':' + str(PORT)}/data"

    # data = {"sensorID": "1", "range": "10"}
    # r = requests.post(url, json=data)
    url = f"{url}?sensorID=1&range=10"
    r = requests.get(url)
    assert r.status_code == 200
# test_arduino_serial_output()


def test_area1_sound():
    # area_map["1"].set_person_detected(True)
    # time.sleep(5)
    # area_map["1"].set_person_detected(False)
    r = None
    url = None
    if HOSTNAME.startswith("https"):
        url = f"{HOSTNAME}/data"
    else:
        url = f"{HOSTNAME + ':' + str(PORT)}/data"

    # data = {"sensorID": "1", "range": "10"}
    # r = requests.post(url, json=data)
    start_url = f"{url}?sensorID=1&range=100"
    r = requests.get(start_url)
    # print(r.json())
    assert r.status_code == 200

    time.sleep(3)

    stop_url = f"{url}?sensorID=1&range=10"
    r = requests.get(stop_url)
    assert r.status_code == 200


test_area1_sound()
