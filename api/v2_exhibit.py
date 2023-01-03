from datetime import datetime as dt
import time
from subprocess import Popen, PIPE

FFMPEG_OUT = open("/tmp/ffmpeg_out", 'a+')
FFMPEG_ERR = open("/tmp/ffmpeg_err", 'a+')
audio_log = open('/tmp/play_audio.log', 'a+')


class ExhibitAreaV2:
    def __init__(self, id, playlist, approx_floor_height=240):
        self.sound_id = id
        # self.motion_id = id
        self.playlist = playlist
        self.person_detected = False
        self.proc = None
        self.ip = None
        self.video_stream = None

    def set_person_detected(self, person_detected):
        self.person_detected = person_detected
        if self.proc and self.person_detected == False:
            self.proc.terminate()

    def play_audio(self):

        artist = self.get_artist_by_time(dt.now())
        # artist = "4"
        channel = int(self.sound_id) - 1
        audio_file = self.playlist[artist][channel]

        cmd = ""
        if artist != "4":
            cmd = f'ffmpeg -i {audio_file} -ac 16 -filter_complex "[0:a]loudnorm=I=-14:LRA=5:TP=-1.5[a];[a]pan=16c|c{channel}=c0[b];[b]volume=1.4[c]" -map "[c]" -f audiotoolbox -audio_device_index 1 -'
        else:
            cmd = f'ffmpeg -i {audio_file} -ac 16 -filter_complex "[0:a]loudnorm=I=-14:LRA=5:TP=-1.5[a];[a]pan=16c|c{channel}=c0[b];[b]volume=1.2[c]" -map "[c]" -f audiotoolbox -audio_device_index 1 -'

        while self.person_detected:
            audio_log.write(f"{dt.now()}\n{cmd}\n" + ("-"*80) + '\n')

            self.proc = Popen(
                cmd, shell=True, stdout=FFMPEG_OUT, stderr=FFMPEG_ERR)
            self.proc.wait()

    def get_artist_by_time(self, now) -> str:
        for h in range(11, 21, 2):
            if now.hour < h and now.minute < 30:
                return "1"
            if now.hour < h and now.minute >= 30:
                return "2"
            if now.hour < h + 1 and now.minute < 30:
                return "3"
            if now.hour < h + 1 and now.minute >= 30:
                return "4"
        return "4"

        # times = [
        #     dt(2022, 1, 1, 10, 0),
        #     dt(2022, 1, 1, 10, 30),
        #     dt(2022, 1, 1, 11, 0),
        #     dt(2022, 1, 1, 11, 30),
        # ]
        # for t in times:
        #     print(get_artist_by_time(t))
