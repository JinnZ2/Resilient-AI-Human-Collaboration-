#!/usr/bin/env bash
set -e
sudo apt update
sudo apt install -y python3-venv python3-pip ffmpeg yt-dlp aria2 jq sox pulseaudio
echo "OK"
