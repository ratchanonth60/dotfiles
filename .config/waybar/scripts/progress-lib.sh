#!/bin/bash

make_bar() {
  local value=${1:-0}
  local width=${2:-8}
  local fill=${3:-█}
  local partial=${4:-▓}
  local empty=${5:-▒}
  local i full_cells remainder

  if [ "$value" -lt 0 ] 2>/dev/null; then
    value=0
  fi

  if [ "$value" -gt 100 ] 2>/dev/null; then
    value=100
  fi

  full_cells=$((value * width / 100))
  remainder=$(((value * width) % 100))

  printf '['
  for ((i = 0; i < width; i++)); do
    if [ "$i" -lt "$full_cells" ]; then
      printf '%s' "$fill"
    elif [ "$i" -eq "$full_cells" ] && [ "$remainder" -gt 0 ] && [ "$full_cells" -lt "$width" ]; then
      printf '%s' "$partial"
    else
      printf '%s' "$empty"
    fi
  done
  printf ']'
}

json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}
