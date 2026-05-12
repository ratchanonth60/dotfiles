#!/bin/bash

. "$HOME/.config/waybar/scripts/progress-lib.sh"

read -r _ user nice system idle iowait irq softirq steal _ < /proc/stat
total1=$((user + nice + system + idle + iowait + irq + softirq + steal))
idle1=$((idle + iowait))

sleep 0.2

read -r _ user nice system idle iowait irq softirq steal _ < /proc/stat
total2=$((user + nice + system + idle + iowait + irq + softirq + steal))
idle2=$((idle + iowait))

delta_total=$((total2 - total1))
delta_idle=$((idle2 - idle1))

if [ "$delta_total" -le 0 ]; then
  usage=0
else
  usage=$(((100 * (delta_total - delta_idle)) / delta_total))
fi

bar=$(make_bar "$usage" 8)
tooltip=$(json_escape "CPU usage: $usage%")
printf '{"text":"[ CPU  %s %3s%% ]","tooltip":"%s"}\n' "$bar" "$usage" "$tooltip"
