#!/bin/bash

fan="$1"

case "$fan" in
  cpu)
    value=$(sensors 2>/dev/null | awk '/fan1:/ {print $2; found=1; exit} END {if (!found) print "0"}')
    ;;
  gpu)
    value=$(sensors 2>/dev/null | awk '/fan2:/ {print $2; found=1; exit} END {if (!found) print "0"}')
    ;;
  *)
    value="0"
    ;;
esac

printf '%s RPM\n' "$value"
