#!/bin/bash

if command -v nvidia-smi >/dev/null 2>&1; then
  value=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1)
  if [ -n "$value" ]; then
    printf '%s\n' "$value"
    exit 0
  fi
fi

echo "N/A"
