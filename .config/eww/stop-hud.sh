#!/bin/bash

set -euo pipefail

export EWW_CONFIG_DIR="$HOME/.config/eww"

eww close-all >/dev/null 2>&1 || true

for pid in $(pgrep -af "cava -p $HOME/.config/cava/config" | awk '{print $1}'); do
  kill "$pid"
done

for pid in $(pgrep -af "python(3)? $HOME/.config/eww/scripts/audio/audio_visualizer.py" | awk '{print $1}'); do
  kill "$pid"
done
