import os
import time
import re
from subprocess import Popen, PIPE


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


def play_audio(file, channel):
    cmd = f'ffmpeg -i {file} -ac 16 -filter_complex "[0:a]pan=16c|c{int(channel) -1}=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -'
    p = Popen(cmd, shell=True)
    time.sleep(2)
    p.terminate()


def test_all_audio():
    playlist = find_audio_files()
    for artist in playlist.keys():
        for i in range(16):
            sound_id = i + 1
            audio_file = playlist[artist][i]
            print(f'Playing {audio_file} on channel {sound_id}')
            play_audio(audio_file, sound_id)
