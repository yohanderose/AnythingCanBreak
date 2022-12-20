import os
import time
import re
from subprocess import Popen, PIPE


SOUNDS_DIR = os.path.join(os.path.dirname(__file__), '../api/sounds')


def find_audio_file(id) -> str:
    files = os.listdir(SOUNDS_DIR)
    for file in files:
        if re.match(f"SPEAKER{id}_.*", file):
            return os.path.join(SOUNDS_DIR, file)

    return "file not found"


FILES = [find_audio_file(i+1) for i in range(16)]


def play_audio(file, channel):
    cmd = f'ffmpeg -i {file} -ac 16 -filter_complex "[0:a]pan=16c|c{int(channel) -1}=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -'
    p = Popen(cmd, shell=True)
    time.sleep(2)
    p.terminate()


def test_all_audio():
    for i in range(len(FILES)):
        audio_file = FILES[i]
        sound_id = i + 1
        print(f'Playing {audio_file} on channel {sound_id}')
        play_audio(audio_file, sound_id)
