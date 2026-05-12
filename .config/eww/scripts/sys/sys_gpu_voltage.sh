#!/bin/bash

value=$(sensors 2>/dev/null | awk '/vddgfx/ {print $2 " mV"; found=1; exit} END {if (!found) print "N/A"}')
printf '%s\n' "$value"
