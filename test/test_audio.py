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


playlist = find_audio_files()


def play_audio(file, channel, duration=2):
    cmd = f'ffmpeg -i {file} -ac 16 -filter_complex "[0:a]pan=16c|c{int(channel) -1}=c0[a];[a]dynaudnorm=p=0.9:s=5[a_norm]" -map "[a_norm]" -f audiotoolbox -audio_device_index 1 -'
    p = Popen(cmd, shell=True)
    time.sleep(duration)
    fade_out(p, channel)


def fade_out(proc, channel):
    if proc:
        # Kill ffmpeg process and fade audio out
        cmd = f'ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 1 -ac 16 -filter_complex "[0:a]pan=16c|c{int(channel) -1}=c0[a];[a]afade=t=out:st=0:d=1[b]" -map "[b]" -f audiotoolbox -audio_device_index 1 -'
        fade = Popen(cmd, shell=True)
        proc.send_signal(2)
        proc.terminate()


# def test_all_speaker():
#     artist = "4"
#     for i in range(16):
#         sound_id = i + 1
#         audio_file = playlist[artist][i]
#         print(f'Playing {audio_file} on channel {sound_id}')
#         play_audio(audio_file, sound_id, duration=10)


def test_all_audio():
    for artist in playlist.keys():
        for i in range(16):
            sound_id = i + 1
            audio_file = playlist[artist][i]
            print(f'Playing {audio_file} on channel {sound_id}')
            play_audio(audio_file, sound_id, duration=5)
