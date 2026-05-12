#!/bin/bash

. "$HOME/.config/waybar/scripts/progress-lib.sh"

battery_dir=$(for path in /sys/class/power_supply/BAT*; do
  if [ -e "$path" ]; then
    printf '%s\n' "$path"
    break
  fi
done)

if [ -z "$battery_dir" ]; then
  printf '{"text":"[ BAT  %s N/A ]","tooltip":"Battery not found","class":"critical"}\n' "$(make_bar 0 8)"
  exit 0
fi

capacity=$(cat "$battery_dir/capacity" 2>/dev/null)
status=$(cat "$battery_dir/status" 2>/dev/null)

if [ -z "$capacity" ]; then
  capacity=0
fi

bar=$(make_bar "$capacity" 8)
class=""
label="BAT"

case "$status" in
  Charging)
    label="CHG"
    ;;
  Full)
    label="FULL"
    ;;
esac

if [ "$capacity" -le 10 ]; then
  class="critical"
elif [ "$capacity" -le 20 ]; then
  class="warning"
fi

tooltip=$(json_escape "Battery: $capacity% ($status)")

if [ -n "$class" ]; then
  printf '{"text":"[ %s  %s %3s%% ]","tooltip":"%s","class":"%s"}\n' "$label" "$bar" "$capacity" "$tooltip" "$class"
else
  printf '{"text":"[ %s  %s %3s%% ]","tooltip":"%s"}\n' "$label" "$bar" "$capacity" "$tooltip"
fi
