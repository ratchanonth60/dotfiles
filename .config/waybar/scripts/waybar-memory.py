#!/usr/bin/env python3

from pathlib import Path

from monitor_suite import COLORS, format_gib, pct_color, print_json, read_int, read_text, span, temp_color

MEM_ICON = ""


def meminfo():
    data = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        data[key] = int(value.strip().split()[0]) * 1024
    return data


def memory_temps():
    modules = []
    index = 1
    for hwmon in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
        name = read_text(hwmon / "name")
        if name not in {"spd5118", "jc42", "dram"}:
            continue
        temps = [read_int(path, 1000) for path in hwmon.glob("temp*_input")]
        temps = [temp for temp in temps if temp and temp > 0]
        if not temps:
            continue
        modules.append((f"DIMM {index}", max(temps)))
        index += 1
    return modules


def tooltip(percent, used, total, available, cached, buffers, temps):
    lines = [
        f"{span(MEM_ICON, COLORS['green'])} {span('Memory Monitor', COLORS['green'], bold=True)}",
        "─" * 28,
        f"Used:      {span(format_gib(used), pct_color(percent), bold=True)} / {format_gib(total)}",
        f"Available: {span(format_gib(available), COLORS['cyan'])}",
        f"Cached:    {span(format_gib(cached), COLORS['yellow'])}",
        f"Buffers:   {span(format_gib(buffers), COLORS['blue'])}",
    ]

    if temps:
        lines.extend(["", "Module temps:"])
        for label, temp in temps:
            lines.append(f"• {label:<8} {span(f'{temp:.0f}°C', temp_color(temp))}")

    lines.append("")
    lines.append("LMB: btop")
    return "\n".join(lines)


info = meminfo()
total = info.get("MemTotal", 0)
available = info.get("MemAvailable", 0)
cached = info.get("Cached", 0)
buffers = info.get("Buffers", 0)
used = max(0, total - available)
percent = (used * 100 / total) if total else 0
temps = memory_temps()

print_json(
    f"{MEM_ICON} {span(f'{percent:.0f}%', pct_color(percent), bold=True)}",
    tooltip(percent, used, total, available, cached, buffers, temps),
    "memory",
)
