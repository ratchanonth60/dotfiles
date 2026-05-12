#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  net_upload.sh
#  Samples network traffic on a given interface and reports upload usage
#  as a percentage (0–100) of a configured max speed.
# ─────────────────────────────────────────────────────────────────────────────

iface=$(nmcli -t -f DEVICE,TYPE,STATE dev status 2>/dev/null | awk -F: '$2=="wifi" && $3=="connected"{print $1; exit}')
[ -z "$iface" ] && iface=$(ip route 2>/dev/null | awk '/^default/ {print $5; exit}')
[ -z "$iface" ] && iface="wlan0"
max_speed=12500000    # 100 Mbps = 100e6 / 8 (bytes/sec). Adjust if faster.

# First sample
tx1=$(awk -v iface=$iface '$1 ~ iface {gsub(":", "", $1); print $10}' /proc/net/dev)
sleep 1
# Second sample
tx2=$(awk -v iface=$iface '$1 ~ iface {gsub(":", "", $1); print $10}' /proc/net/dev)

bps=$((tx2 - tx1))                 # bytes per second
percent=$((bps * 1000 / max_speed))  # scaled ×10 for sensitivity

# Clamp between 0–100
if [ "$percent" -gt 100 ]; then percent=100; fi
if [ "$percent" -lt 0 ]; then percent=0; fi

echo $percent
