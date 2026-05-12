#!/bin/bash

status=$(omarchy-weather-status 2>/dev/null)
status=${status//$'\n'/ }

escape_json() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

if [ -z "$status" ]; then
  printf '{"text":"","class":"unavailable"}\n'
  exit 0
fi

temp=$(printf '%s' "$status" | sed -n 's/.*Temp \([-0-9]\+\).*/\1/p')
if [ -n "$temp" ]; then
  text="[WX ${temp}C]"
else
  text="[WX]"
fi

tooltip=$(printf '%s' "$status" | LC_ALL=C sed 's/[^ -~]/ /g; s/  */ /g; s/^ //; s/ $//')
tooltip=$(escape_json "$tooltip")
printf '{"text":"%s","tooltip":"%s"}\n' "$text" "$tooltip"
