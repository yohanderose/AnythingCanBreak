#! /usr/bin/bash
# ffmpeg play audio_file on specified channel of speaker
audio_file=$1
output_channel=$2
output_device=1

# Dims the speaker before killing ffmpeg_pid
# returns the volume level to the original level
function fade_out  {
	# get the current volume
	current_volume=$(amixer -c $output_device sget Master | grep -o -P '(?<=\[)[0-9]+(?=%\])')

	for ((i=$current_volume; i>=0; i-=10)); do
		amixer -c $output_device sset Master $i%
		sleep 0.1
	done

	# kill the process
	kill -9 $(ps -aux | grep "ffmpeg.*api/sound/4/speaker1.wav" | grep -v grep | awk '{print $2}')
	# reset volume
	amixer -c $output_device sset Master $current_volume%
}

# if linux
if [ "$(uname)" == "Linux" ]; then
	ffmpeg -i $audio_file -ac 2 -filter_complex "[0:a]pan=stereo|c$output_channel=c0[a];[a]dynaudnorm=p=0.9:s=5[a_norm]" -map "[a_norm]" -f alsa hw:$output_device,0 -loglevel quiet &
 
	sleep 2
	fade_out
fi

# if mac
if [ "$(uname -s)" == "Darwin" ]; then
	ffmpeg -i $audio_file -ac 16 -filter_complex "[0:a]pan=16c|c$output_channel=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -
fi
