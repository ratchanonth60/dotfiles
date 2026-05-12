#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  net_vpn.sh
#  Checks if VPN (10.6.0.x) is active, outputs 100 (on) or 0 (off).
#  Example: VPN connected  → 100
#           VPN disconnected → 0
# ─────────────────────────────────────────────────────────────────────────────

if ip a | grep -Eq "10\.6\.|wg[0-9]+|tun[0-9]+"; then
  echo 100
else
  echo 0
fi
