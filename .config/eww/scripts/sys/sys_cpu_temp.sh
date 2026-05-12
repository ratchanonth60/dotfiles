#!/bin/bash

value=$(sensors 2>/dev/null | awk '
  /Package id 0:/ {print $4; found=1; exit}
  /CPU:/ {print $2; found=1; exit}
  END {if (!found) print "N/A"}
')
printf '%s\n' "$value"
