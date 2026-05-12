#!/bin/bash

value=$(sensors 2>/dev/null | awk '/power1:/ {print $2 " " $3; found=1; exit} END {if (!found) print "N/A"}')
printf '%s\n' "$value"
