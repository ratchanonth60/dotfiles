#!/bin/bash

set -euo pipefail

export EWW_CONFIG_DIR="$HOME/.config/eww"

mkdir -p /tmp

eww daemon >/dev/null 2>&1 || true
sleep 1
eww close-all >/dev/null 2>&1 || true

if ! pgrep -af "cava -p $HOME/.config/cava/config" >/dev/null 2>&1; then
  nohup cava -p "$HOME/.config/cava/config" >/tmp/cava.log 2>&1 &
fi

if ! pgrep -af "python(3)? $HOME/.config/eww/scripts/audio/audio_visualizer.py" >/dev/null 2>&1; then
  nohup python "$HOME/.config/eww/scripts/audio/audio_visualizer.py" >/tmp/eww-visualizer.log 2>&1 &
fi

bash "$HOME/.config/eww/scripts/ascii/ascii_live_log.sh" >/dev/null 2>&1 || true

eww open-many \
  active_workspace \
  ascii_decor_frame \
  audio_status \
  cpu_ram_storage_bars \
  four_boxes \
  net_bars \
  orange_workspace \
  power-cooling_header_text \
  power_mode_text \
  right_fan_data \
  right_internet_text \
  visualizer_window \
  welcome_text \
  workspace_window_text
