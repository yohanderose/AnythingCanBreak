#! /bin/sh
audio_file=$1
output_channel=$2
output_device=1


# ffmpeg play audio_file on specified channel of speaker
ffmpeg -i $audio_file -ac 2 -filter_complex "[0:a]pan=stereo|c$output_channel=c0[a]" -map "[a]" -f alsa hw:$output_device,0

