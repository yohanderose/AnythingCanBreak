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
	kill -9 $(ps -aux | grep "ffmpeg.*$audio_file" | grep -v grep | awk '{print $2}')
	# reset volume
	amixer -c $output_device sset Master $current_volume%
}

# if linux
if [ "$(uname)" == "Linux" ]; then
	ffmpeg -i $audio_file -ac 2 -filter_complex "[0:a]loudnorm=I=-16:LRA=5:TP=-1.5[a];[a]pan=stereo|c$output_channel=c0[b]" -map "[b]" -f alsa hw:$output_device,0 &
 
	sleep 20
	fade_out
fi

# if mac
if [ "$(uname -s)" == "Darwin" ]; then
	ffmpeg -i $audio_file -ac 16 -filter_complex "[0:a]pan=16c|c$output_channel=c0[a]" -map "[a]" -f audiotoolbox -audio_device_index 1 -
fi
