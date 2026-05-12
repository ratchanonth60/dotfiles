#!/usr/bin/env python3

import json
import os
import pathlib
import subprocess
import time

try:
    import tomllib
except ImportError:  # pragma: no cover
    tomllib = None


DEFAULT_COLORS = {
    "black": "#1f2335",
    "red": "#f7768e",
    "green": "#9ece6a",
    "yellow": "#e0af68",
    "blue": "#7aa2f7",
    "magenta": "#bb9af7",
    "cyan": "#7dcfff",
    "white": "#c0caf5",
    "bright_black": "#565f89",
    "bright_red": "#ff899d",
    "bright_green": "#b9f27c",
    "bright_yellow": "#ffcf70",
    "bright_blue": "#8db0ff",
    "bright_magenta": "#c7a9ff",
    "bright_cyan": "#a4daff",
    "bright_white": "#ffffff",
}

STATE_DIR = pathlib.Path("/tmp/waybar-monitor-suite")


def load_theme_colors():
    paths = [
        pathlib.Path.home() / ".config/omarchy/current/theme/colors.toml",
        pathlib.Path.home() / ".config/waybar/colors.toml",
    ]
    for theme_path in paths:
        if not tomllib or not theme_path.exists():
            continue
        try:
            data = tomllib.loads(theme_path.read_text())
            colors = data.get("colors", {})
            normal = colors.get("normal", {})
            bright = {f"bright_{k}": v for k, v in colors.get("bright", {}).items()}
            merged = DEFAULT_COLORS.copy()
            merged.update(normal)
            merged.update(bright)
            return merged
        except Exception:
            continue
    return DEFAULT_COLORS.copy()


COLORS = load_theme_colors()


def span(text, color, bold=False):
    weight = " weight='bold'" if bold else ""
    return f"<span foreground='{color}'{weight}>{text}</span>"


def pct_color(value):
    if value is None:
        return COLORS["bright_black"]
    if value < 20:
        return COLORS["blue"]
    if value < 40:
        return COLORS["cyan"]
    if value < 60:
        return COLORS["green"]
    if value < 75:
        return COLORS["yellow"]
    if value < 90:
        return COLORS["bright_yellow"]
    return COLORS["red"]


def temp_color(value):
    if value is None:
        return COLORS["bright_black"]
    if value < 40:
        return COLORS["blue"]
    if value < 50:
        return COLORS["cyan"]
    if value < 65:
        return COLORS["green"]
    if value < 75:
        return COLORS["yellow"]
    if value < 85:
        return COLORS["bright_yellow"]
    return COLORS["red"]


def print_json(text, tooltip, class_name):
    print(
        json.dumps(
            {
                "text": text,
                "tooltip": tooltip,
                "markup": "pango",
                "class": class_name,
            }
        )
    )


def read_text(path):
    try:
        return pathlib.Path(path).read_text().strip()
    except Exception:
        return ""


def read_int(path, scale=1):
    try:
        return int(read_text(path)) / scale
    except Exception:
        return None


def format_bytes(num):
    value = float(num)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def format_rate(num):
    return f"{format_bytes(num)}/s"


def format_gib(num_bytes):
    return f"{num_bytes / (1024 ** 3):.1f} GiB"


def read_state(name):
    path = STATE_DIR / f"{name}.json"
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def write_state(name, data):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (STATE_DIR / f"{name}.json").write_text(json.dumps(data))
    except Exception:
        pass


def ps_lines(sort_key, limit):
    try:
        field = sort_key.lstrip("%")
        output = subprocess.check_output(
            ["ps", "-eo", f"{sort_key},comm", "--sort", f"-{field}", "--no-headers"],
            text=True,
        )
    except Exception:
        return []

    rows = []
    for line in output.splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        value, command = parts
        if command.startswith("waybar"):
            continue
        try:
            rows.append((float(value), command))
        except ValueError:
            continue
        if len(rows) >= limit:
            break
    return rows


def lspci_name(slot, fallback):
    try:
        output = subprocess.check_output(["lspci", "-s", slot], text=True).strip()
        return output.split(": ", 1)[1]
    except Exception:
        return fallback


def runtime_status(device_path):
    value = read_text(pathlib.Path(device_path) / "power/runtime_status")
    return value or "unknown"


def read_hwmon_temps(base_path):
    temps = []
    base = pathlib.Path(base_path)
    for temp_path in sorted(base.glob("temp*_input")):
        temp = read_int(temp_path, 1000)
        if temp is not None and temp > 0:
            temps.append(temp)
    return temps


def now():
    return time.time()
