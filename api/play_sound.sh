#! /bin/sh
# ffmpeg play audio_file on specified channel of speaker
audio_file=$1
output_channel=$2
output_device=1


# if linux
if [ "$(uname)" == "Linux" ]; then
	ffmpeg -i $audio_file -ac 2 -filter_complex "[0:a]pan=stereo|c$output_channel=c0[a];[a]dynaudnorm=p=0.9:s=5[a_norm]" -map "[a_norm]" -f alsa hw:$output_device,0

fi

# if mac
if [ "$(uname -s)" == "Darwin" ]; then
	ffmpeg -i $audio_file -ac 16 -filter_complex "[0:a]pan=16c|c$output_channel=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -
fi
