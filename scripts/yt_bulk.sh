#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-data/videos}"
URL="${2:?channel_or_playlist_url}"
mkdir -p "$DEST"

# sane defaults for rural connection
OPTS="${YTDLP_OPTS:---no-mtime --ignore-errors --yes-playlist --retries 100 --fragment-retries 100}"
yt-dlp -ci -f mp4 -N 4 -o "${DEST}/%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title).150B.%(ext)s" \
  $OPTS "$URL"
