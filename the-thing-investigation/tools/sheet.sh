#!/usr/bin/env bash
# sheet.sh <film> <start> <end> <interval_s|all> <cols>x<rows> <thumb_width> <out_prefix>
# Contact sheets of REAL decoded frames (select filter, no fps resampling), each labelled
# with its true presentation time and frame number (frame = round(t*24000/1001)).
# interval "all" = every frame (true frame-by-frame).
set -euo pipefail
f=$1; s=$2; e=$3; iv=$4; grid=$5; w=$6; out=$7
pre=""; [[ -n ${CROP:-} ]] && pre="crop=${CROP},"   # optional CROP=w:h:x:y (full-res coordinates)
[[ -n ${EQ:-} ]] && pre="${pre}${EQ},"              # optional EQ=<ffmpeg filter>, e.g. eq=gamma=2.2 (brightening dark scenes)
if [[ $iv == all ]]; then sel="select=1"; else sel="select='isnan(prev_selected_t)+gte(t-prev_selected_t-0.0005\,$iv)'"; fi
ffmpeg -v error -y -ss "$s" -to "$e" -copyts -i "$f" -fps_mode passthrough -vf "$sel,${pre}scale=$w:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:text='%{pts\:hms} f%{eif\:round(t*24000/1001)\:d}':x=4:y=4:fontsize=$((w/22)):fontcolor=yellow:box=1:boxcolor=black@0.6,tile=$grid:padding=2:color=gray" -q:v 3 "${out}_%02d.jpg"
ls "${out}"_*.jpg
