#!/bin/bash

mode=$(powerprofilesctl get 2>/dev/null)

case "$mode" in
  performance) echo "PERF" ;;
  balanced) echo "BAL" ;;
  power-saver) echo "SAVE" ;;
  *) echo "N/A" ;;
esac
