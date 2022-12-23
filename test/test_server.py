import pytest
import os
import time
import requests
from flask import jsonify
from dotenv import load_dotenv
from subprocess import Popen, PIPE

load_dotenv()

HOSTNAME = f"http://{os.getenv('HOST_IP')}"
# HOSTNAME = "https://0a80-2001-44c8-4134-762-da69-323d-eb95-3fba.ngrok.io"
PORT = 5000
proc = None


def test_server():
    r = None
    if HOSTNAME.startswith("https"):
        r = requests.get(HOSTNAME)
    else:
        r = requests.get(HOSTNAME + ":" + str(PORT))
    assert r.status_code == 200


def test_request():
    r = None
    url = None
    if HOSTNAME.startswith("https"):
        url = f"{HOSTNAME}/data"
    else:
        url = f"{HOSTNAME + ':' + str(PORT)}/data"

    # data = {"sensorID": "1", "range": "10"}
    # r = requests.post(url, json=data)
    url = f"{url}?sensorID=1&range=0&motion=0"
    r = requests.get(url)
    assert r.status_code == 200

# test_arduino_serial_output()


def test_area1_api():
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
    start_url = f"{url}?sensorID=4&range=100&motion=1"
    r = requests.get(start_url)
    # print(r.json())
    assert r.status_code == 200

    time.sleep(2)

    stop_url = f"{url}?sensorID=4&range=0&motion=0"
    r = requests.get(stop_url)
    assert r.status_code == 200


# test_area1_api()
