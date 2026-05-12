#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
from pathlib import Path

from monitor_suite import (
    COLORS,
    format_gib,
    format_rate,
    now,
    pct_color,
    print_json,
    read_int,
    read_state,
    read_text,
    span,
    temp_color,
    write_state,
)

STORAGE_ICON = ""


def lsblk_tree():
    output = subprocess.check_output(
        ["lsblk", "-J", "-b", "-o", "NAME,PATH,TYPE,MOUNTPOINT,FSTYPE,SIZE,MODEL"],
        text=True,
    )
    return json.loads(output)["blockdevices"]


def flatten(nodes):
    for node in nodes:
        yield node
        for child in node.get("children", []) or []:
            yield from flatten([child])


def base_disk(name):
    if name.startswith("nvme"):
        return re.sub(r"p\d+$", "", name)
    return re.sub(r"\d+$", "", name)


def root_temp(disk_name):
    direct = Path("/sys/class/block") / disk_name / "device" / "hwmon"
    for hwmon in sorted(direct.glob("hwmon*")):
        temps = [read_int(path, 1000) for path in hwmon.glob("temp*_input")]
        temps = [temp for temp in temps if temp and temp > 0]
        if temps:
            return max(temps)

    for hwmon in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        name = read_text(hwmon / "name")
        if disk_name.startswith("nvme") and name == "nvme":
            temps = [read_int(path, 1000) for path in hwmon.glob("temp*_input")]
            temps = [temp for temp in temps if temp and temp > 0]
            if temps:
                return min(temps)
    return None


def disk_bytes(disk_name):
    stat_path = Path("/sys/class/block") / disk_name / "stat"
    try:
        fields = stat_path.read_text().split()
        read_bytes = int(fields[2]) * 512
        write_bytes = int(fields[6]) * 512
        return read_bytes, write_bytes
    except Exception:
        return None, None


def io_rates(disk_name):
    current_read, current_write = disk_bytes(disk_name)
    timestamp = now()
    state = read_state(f"storage-{disk_name}")
    prev_read = state.get("read")
    prev_write = state.get("write")
    prev_time = state.get("time")
    write_state(f"storage-{disk_name}", {"read": current_read, "write": current_write, "time": timestamp})

    if None in {current_read, current_write, prev_read, prev_write, prev_time}:
        return 0.0, 0.0

    delta = max(timestamp - prev_time, 0.001)
    return max(0.0, (current_read - prev_read) / delta), max(0.0, (current_write - prev_write) / delta)


def mounts():
    entries = []
    for node in flatten(lsblk_tree()):
        mountpoint = node.get("mountpoint")
        if not mountpoint or mountpoint in {"/boot"}:
            continue
        if node.get("type") != "part":
            continue
        if mountpoint.startswith(("/proc", "/sys", "/run", "/dev")):
            continue
        usage = shutil.disk_usage(mountpoint)
        percent = (usage.used * 100 / usage.total) if usage.total else 0
        disk_name = base_disk(node["name"])
        read_rate, write_rate = io_rates(disk_name)
        entries.append(
            {
                "label": "Root" if mountpoint == "/" else mountpoint,
                "mountpoint": mountpoint,
                "filesystem": node.get("fstype") or "unknown",
                "size": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": percent,
                "disk_name": disk_name,
                "model": (node.get("model") or read_text(Path("/sys/class/block") / disk_name / "device/model")).strip(),
                "temperature": root_temp(disk_name),
                "read_rate": read_rate,
                "write_rate": write_rate,
            }
        )
    return entries


def tooltip(entries):
    lines = [
        f"{span(STORAGE_ICON, COLORS['blue'])} {span('Storage Monitor', COLORS['blue'], bold=True)}",
        "─" * 34,
    ]
    for entry in entries:
        lines.append(span(f"{entry['label']} • {entry['filesystem']}", COLORS["white"], bold=True))
        lines.append(
            f"• Used: {span(format_gib(entry['used']), pct_color(entry['percent']), bold=True)} / {format_gib(entry['size'])}"
        )
        lines.append(f"• Free: {span(format_gib(entry['free']), COLORS['cyan'])}")
        lines.append(
            f"• I/O:  {span(format_rate(entry['read_rate']), COLORS['blue'])} read • "
            f"{span(format_rate(entry['write_rate']), COLORS['green'])} write"
        )
        if entry["temperature"] is not None:
            lines.append(f"• Temp: {span(f'{entry['temperature']:.0f}°C', temp_color(entry['temperature']))}")
        if entry["model"]:
            lines.append(f"• Disk: {entry['model']}")
        lines.append("")
    lines.append("LMB: open /")
    return "\n".join(lines)


entries = mounts()
root = next((entry for entry in entries if entry["mountpoint"] == "/"), entries[0] if entries else None)
percent = root["percent"] if root else 0

print_json(
    f"{STORAGE_ICON} {span(f'{percent:.0f}%', pct_color(percent), bold=True)}",
    tooltip(entries if entries else [{"label": "No mounted disks", "filesystem": "", "used": 0, "size": 1, "free": 0, "percent": 0, "read_rate": 0, "write_rate": 0, "temperature": None, "model": "", "mountpoint": "/"}]),
    "storage",
)
