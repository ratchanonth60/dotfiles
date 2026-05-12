#!/bin/bash

status=$(omarchy-update-available 2>/dev/null)
status=${status//$'\n'/ }

escape_json() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

if printf '%s' "$status" | grep -qi 'up to date'; then
  tooltip=$(escape_json "$status")
  printf '{"text":"[SYS OK]","tooltip":"%s"}\n' "$tooltip"
elif [ -n "$status" ]; then
  tooltip=$(escape_json "$status")
  printf '{"text":"[UPDATE]","tooltip":"%s","class":"active"}\n' "$tooltip"
else
  printf '{"text":""}\n'
fi
