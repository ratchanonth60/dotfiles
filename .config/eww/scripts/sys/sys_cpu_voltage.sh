#!/bin/bash

value=$(sensors 2>/dev/null | awk '
  /Vcore:|vcore:|SVI3_Core:/ {print $2 " V"; found=1; exit}
  END {if (!found) print "N/A"}
')
printf '%s\n' "$value"
