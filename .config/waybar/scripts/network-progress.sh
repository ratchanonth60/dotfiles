#!/bin/bash

. "$HOME/.config/waybar/scripts/progress-lib.sh"

active_wifi=$(nmcli -t -f active,ssid,signal dev wifi 2>/dev/null | awk -F: '$1=="yes"{print $2 "|" $3; exit}')

if [ -n "$active_wifi" ]; then
  ssid=${active_wifi%|*}
  signal=${active_wifi##*|}
  bar=$(make_bar "$signal" 8)
  tooltip=$(json_escape "WiFi: $ssid ($signal%)")
  printf '{"text":"[ WIFI %s %3s%% ]","tooltip":"%s"}\n' "$bar" "$signal" "$tooltip"
  exit 0
fi

ethernet=$(nmcli -t -f DEVICE,TYPE,STATE dev status 2>/dev/null | awk -F: '$2=="ethernet" && $3=="connected"{print $1; exit}')

if [ -n "$ethernet" ]; then
  tooltip=$(json_escape "Ethernet: $ethernet connected")
  printf '{"text":"[ ETH  %s ]","tooltip":"%s"}\n' "$(make_bar 100 8)" "$tooltip"
  exit 0
fi

printf '{"text":"[ NET  %s ]","tooltip":"Disconnected","class":"disconnected"}\n' "$(make_bar 0 8)"
