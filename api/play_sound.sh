#! /bin/sh
audio_file=$1
channel_number=$2

# get the channel number in hex with leading zero
channel_hex=$(printf "%02x" $channel_number)

# ffmpeg play audio_file on audiotoolbox device 1, only on channel 0
 ffmpeg -i $audio_file -f audiotoolbox -audio_device_index 1 -map_channel 0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0 -



