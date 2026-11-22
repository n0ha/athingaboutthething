#!/usr/bin/env bash
# vm.sh — run video decoding on the Hetzner analysis VM, bring back only small results.
# The laptop must not decode the film (2026-11-21 an unbounded job got the terminal OOM-killed).
#
#   vm.sh sheet <start> <end> <interval_s|all> <cols>x<rows> <thumb_w> <local_out_prefix>
#         (env CROP=w:h:x:y crops in full-res pixels before scaling; env EQ=<ffmpeg filter>
#          brightens, e.g. EQ=eq=gamma=2.2 — say so when you cite an enhanced image)
#   vm.sh frame <HH:MM:SS.mmm> <local_out.png|.jpg> [crop=w:h:x:y] [zoom]
#         one full-res frame (input-side -ss is frame-accurate); optional crop and integer zoom
#   vm.sh run '<shell command>'      run on the VM (film: /data/src/film.mkv, tools: /data/tools)
#   vm.sh get <remote_path> <local_dir>   copy files back
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
CFG="$HERE/../../work/vm/ssh_config"
S() { ssh -F "$CFG" -o BatchMode=yes thething "$@"; }
FILM=/data/src/film.mkv
cmd=${1:?usage}; shift
LOCAL_FILM="$HERE/../../work/film.mkv"
# Until the film is on the VM, fall back to the laptop, strictly capped: one extraction at a
# time (flock), max 1.5 GB RAM and 1.5 cores, lowest priority.
LOCAL=0
if [[ $cmd == sheet || $cmd == frame ]] && ! S "test -s $FILM"; then LOCAL=1; fi
capped() { flock /tmp/thething-local-decode.lock systemd-run --user --scope -q -p MemoryMax=1500M -p MemorySwapMax=0 -p CPUQuota=150% nice -n 15 ionice -c3 "$@"; }
case $cmd in
  sheet)
    s=$1; e=$2; iv=$3; grid=$4; w=$5; out=$6
    mkdir -p "$(dirname "$out")"; base=$(basename "$out")
    if (( LOCAL )); then
      CROP="${CROP:-}" EQ="${EQ:-}" capped "$HERE/sheet.sh" "$LOCAL_FILM" "$s" "$e" "$iv" "$grid" "$w" "$out"
    else
      tmp=$(S mktemp -d)
      S "CROP=$(printf %q "${CROP:-}") EQ=$(printf %q "${EQ:-}") nice -n 5 /data/tools/sheet.sh $FILM $(printf '%q ' "$s" "$e" "$iv" "$grid" "$w") $tmp/x >/dev/null"
      S "cd $tmp && tar cf - ." | tar xf - -C "$(dirname "$out")" --transform "s|^\./x_|${base}_|"
      S "rm -rf $tmp"; ls "$(dirname "$out")/${base}"_*.jpg
    fi ;;
  frame)
    t=$1; out=$2; crop=${3:-}; zoom=${4:-1}
    mkdir -p "$(dirname "$out")"; ext=${out##*.}
    vf=""; [[ -n $crop ]] && vf="${crop#crop=}" && vf="crop=$vf"
    if [[ $zoom != 1 ]]; then vf="${vf:+$vf,}scale=iw*$zoom:ih*$zoom:flags=lanczos"; fi
    [[ -n ${EQ:-} ]] && vf="${vf:+$vf,}$EQ"   # optional EQ=<ffmpeg filter>, e.g. eq=gamma=2.2
    codec=$([[ $ext == png ]] && echo png || echo mjpeg)
    if (( LOCAL )); then
      capped ffmpeg -v error -threads 1 -ss "$t" -i "$LOCAL_FILM" -frames:v 1 ${vf:+-vf "$vf"} -q:v 2 -f image2 -c:v $codec - > "$out"
    else
      S "ffmpeg -v error -ss $(printf %q "$t") -i $FILM -frames:v 1 ${vf:+-vf $(printf %q "$vf")} -q:v 2 -f image2 -c:v $codec -" > "$out"
    fi
    echo "$out" ;;
  run) S "$@" ;;
  get) mkdir -p "$2"; rsync -a -e "ssh -F $CFG" "thething:$1" "$2/" ;;
  *) echo "unknown command $cmd" >&2; exit 2 ;;
esac
