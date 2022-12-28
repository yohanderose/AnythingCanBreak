import os
import time
from datetime import datetime as dt
import requests
from concurrent.futures import ThreadPoolExecutor
import random
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

HOST_IP = os.getenv("HOST_IP")


def ping_python_api(i) -> float:
    url = f'http://{HOST_IP}:5000/data?range=100&motion=0'
    start = dt.now()
    init_response = requests.get(url)
    assert init_response.status_code == 200
    url = f'http://{HOST_IP}:5000/data?range=0&motion=0'
    stop_response = requests.get(url)
    assert stop_response.status_code == 200
    return (dt.now() - start).microseconds / 1000


def ping_python_apiv2(i) -> float:
    rand_id = random.randint(1, 16)
    url = f'http://{HOST_IP}:5000/{rand_id}?sensorID={rand_id}&range=100&motion=0'
    start = dt.now()
    init_response = requests.get(url)
    assert init_response.status_code == 200
    url = f'http://{HOST_IP}:5000/{rand_id}?sensorID={rand_id}&range=0&motion=0'
    stop_response = requests.get(url)
    assert stop_response.status_code == 200
    return (dt.now() - start).microseconds / 1000


def ping_go_api(i) -> float:
    url = f'http://{HOST_IP}:3000/data?range=100&motion=0'
    start = dt.now()
    init_response = requests.get(url)
    assert init_response.status_code == 200
    url = f'http://{HOST_IP}:3000/data?range=0&motion=0'
    stop_response = requests.get(url)
    assert stop_response.status_code == 200
    return (dt.now() - start).microseconds / 1000


def ping_go_apiv2(i) -> float:
    rand_id = random.randint(1, 16)
    url = f'http://{HOST_IP}:3000/{rand_id}?sensorID={rand_id}&range=100&motion=0'
    start = dt.now()
    init_response = requests.get(url)
    assert init_response.status_code == 200
    url = f'http://{HOST_IP}:3000/{rand_id}?sensorID={rand_id}&range=0&motion=0'
    stop_response = requests.get(url)
    assert stop_response.status_code == 200
    return (dt.now() - start).microseconds / 1000


def ping_all(i):
    return ping_python_api(i), ping_python_apiv2(i), ping_go_api(i), ping_go_apiv2(i)


def run_compare_server(n):
    # Make n concurrent requests to each server and return the average response time
    response_times = []

    with ThreadPoolExecutor(max_workers=30) as executor:
        response_times = list(executor.map(ping_all, range(n)))

    python_avg = sum([x[0] for x in response_times]) / len(response_times)
    python_v2_avg = sum([x[1] for x in response_times]) / len(response_times)
    go_avg = sum([x[2] for x in response_times]) / len(response_times)
    go_v2_avg = sum([x[3] for x in response_times]) / len(response_times)

    assert len(response_times) > 0
    return python_avg, python_v2_avg, go_avg, go_v2_avg


def test_batch_compare(batches=10, n=10_000):

    avgs = []
    for _ in tqdm(range(batches)):
        avgs.append(run_compare_server(n))

    python_avg = sum([x[0] for x in avgs]) / len(avgs)
    python_v2_avg = sum([x[1] for x in avgs]) / len(avgs)
    go_avg = sum([x[2] for x in avgs]) / len(avgs)
    go_v2_avg = sum([x[3] for x in avgs]) / len(avgs)

    print(f'Python average response time: {python_avg}ms')
    print(f'Python v2 average response time: {python_v2_avg}ms')
    print(f'Go average response time: {go_avg}ms')
    print(f'Go v2 average response time: {go_v2_avg}ms')


test_batch_compare(n=1000)
