#!/bin/bash

. "$HOME/.config/waybar/scripts/progress-lib.sh"

mute=$(pactl get-sink-mute @DEFAULT_SINK@ 2>/dev/null | awk '{print $2}')
volume=$(pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null | head -1 | grep -o '[0-9]\+%' | head -1 | tr -d '%')

if [ -z "$volume" ]; then
  volume=0
fi

bar=$(make_bar "$volume" 8)
tooltip=$(json_escape "Volume: $volume%")

if [ "$mute" = "yes" ]; then
  printf '{"text":"[ VOL  %s MUT ]","tooltip":"Muted","class":"muted"}\n' "$(make_bar 0 8)"
else
  printf '{"text":"[ VOL  %s %3s%% ]","tooltip":"%s"}\n' "$bar" "$volume" "$tooltip"
fi
