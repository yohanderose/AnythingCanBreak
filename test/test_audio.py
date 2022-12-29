import os
import time
import re
from subprocess import Popen, PIPE
from sys import platform
from concurrent.futures import ThreadPoolExecutor


SOUNDS_DIR = os.path.join(os.path.dirname(__file__), '../api/sound')


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


def play_audio(data, duration=2):
    file = data['file']
    channel = data['channel']
    duration = data['duration']
    # if osx
    cmd = ""
    if platform == "darwin":
        cmd = f'ffmpeg -i {file} -ac 16 -filter_complex "[0:a]loudnorm=I=-16:LRA=5:TP=-1.5[a];[a]pan=stereo|c{int(channel) - 1}=c0[b]" -map "[b]" -f audiotoolbox -audio_device_index 1 -'
    elif platform == "linux":
        cmd = f'ffmpeg -i {file} -ac 2 -filter_complex "[0:a]loudnorm=I=-16:LRA=5:TP=-1.5[a];[a]pan=stereo|c{int(channel) - 1}=c0[b]" -map "[b]" -f alsa default'
    # if linux

    p = Popen(cmd, shell=True)
    time.sleep(duration)
    fade_out(p, channel)


def fade_out(proc, channel):
    if proc:
        # # Kill ffmpeg process and fade audio out
        # cmd = f'ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 1 -ac 16 -filter_complex "[0:a]pan=16c|c{int(channel) -1}=c0[a];[a]afade=t=out:st=0:d=1[b]" -map "[b]" -f audiotoolbox -audio_device_index 1 -'
        # fade = Popen(cmd, shell=True)
        proc.terminate()


def test_concurrent_audio():
    test = (
        {'file': playlist["4"][0], 'channel': 1, 'duration': 4},
        {'file': playlist["4"][1], 'channel': 2, 'duration': 4},
    )

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(play_audio, test)


# def test_all_audio():
#     for artist in playlist.keys():
#         for i in range(16):
#             sound_id = i + 1
#             audio_file = playlist[artist][i]
#             print(f'Playing {audio_file} on channel {sound_id}')
#             play_audio(
#                 {'file': audio_file, 'channel': sound_id, 'duration': 5})
