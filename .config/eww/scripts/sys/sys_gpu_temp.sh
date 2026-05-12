#!/bin/bash

if command -v nvidia-smi >/dev/null 2>&1; then
  value=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null | head -1)
  if [ -n "$value" ]; then
    printf '+%s°C\n' "$value"
    exit 0
  fi
fi

value=$(sensors 2>/dev/null | awk '/GPU:/ {print $2; found=1; exit} END {if (!found) print "N/A"}')
printf '%s\n' "$value"
