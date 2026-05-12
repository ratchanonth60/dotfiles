#!/usr/bin/env bash
# ~/.config/eww/scripts/net/net_vpn_status.sh
# Show VPN status + country (for Eww)

if ip a | grep -Eq "10\.6\.|wg[0-9]+|tun[0-9]+"; then
  echo "[ФАНТОМ]"
else
  echo "KAPUTT"
fi
