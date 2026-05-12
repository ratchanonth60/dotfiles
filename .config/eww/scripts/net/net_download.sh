#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  net_download.sh
#  Samples network traffic on a given interface and reports download usage
#  as a percentage (0–100) of a configured max speed.
#  
#  Usage: ./net_download.sh
#  Example: output "42" → meaning 42% of max throughput.
#
# ─────────────────────────────────────────────────────────────────────────────

iface=$(nmcli -t -f DEVICE,TYPE,STATE dev status 2>/dev/null | awk -F: '$2=="wifi" && $3=="connected"{print $1; exit}')
[ -z "$iface" ] && iface=$(ip route 2>/dev/null | awk '/^default/ {print $5; exit}')
[ -z "$iface" ] && iface="wlan0"
max_speed=12500000   # adjust: this is 100 Mbps (100*1e6 / 8)

# First sample
rx1=$(awk -v iface=$iface '$1 ~ iface {gsub(":", "", $1); print $2}' /proc/net/dev)
sleep 1
# Second sample
rx2=$(awk -v iface=$iface '$1 ~ iface {gsub(":", "", $1); print $2}' /proc/net/dev)

bps=$((rx2 - rx1))              # bytes per second
percent=$((bps * 100 / max_speed))

# Clamp between 0–100
if [ "$percent" -gt 100 ]; then percent=100; fi
if [ "$percent" -lt 0 ]; then percent=0; fi

echo $percent
