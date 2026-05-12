#!/usr/bin/env bash

value=$(sensors 2>/dev/null | awk '
  /ucsi_source_psy/ {in_ucsi=1; next}
  in_ucsi && /in0:/ && $2 != "0.00" {print $2 " V"; found=1; exit}
  END {if (!found) print "N/A"}
')
printf '%s\n' "$value"
