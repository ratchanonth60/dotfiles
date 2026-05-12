#!/bin/bash

wifi_if=$(nmcli -t -f DEVICE,TYPE,STATE dev status 2>/dev/null | awk -F: '$2=="wifi" && $3=="connected"{print $1; exit}')
[ -z "$wifi_if" ] && wifi_if="offline"

cat > /tmp/live_text.txt <<EOF
reactor online
profile $(powerprofilesctl get 2>/dev/null || echo unknown)
net $wifi_if
EOF
