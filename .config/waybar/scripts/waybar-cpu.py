#!/usr/bin/env python3

from pathlib import Path

from monitor_suite import (
    COLORS,
    now,
    pct_color,
    print_json,
    ps_lines,
    read_int,
    read_state,
    read_text,
    span,
    temp_color,
    write_state,
)

CPU_ICON = ""


def read_cpu_times():
    lines = Path("/proc/stat").read_text().splitlines()
    totals = {}
    for line in lines:
        if not line.startswith("cpu"):
            continue
        parts = line.split()
        label = parts[0]
        values = [int(value) for value in parts[1:]]
        total = sum(values)
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        totals[label] = {"total": total, "idle": idle}
    return totals


def cpu_usage():
    current = read_cpu_times()
    state = read_state("cpu")
    previous = state.get("times", {})

    def calc(label):
        cur = current.get(label)
        prev = previous.get(label)
        if not cur or not prev:
            return 0.0
        total_delta = cur["total"] - prev["total"]
        idle_delta = cur["idle"] - prev["idle"]
        if total_delta <= 0:
            return 0.0
        return max(0.0, min(100.0, (total_delta - idle_delta) * 100.0 / total_delta))

    overall = calc("cpu")
    per_core = [calc(label) for label in sorted(current) if label.startswith("cpu") and label != "cpu"]
    write_state("cpu", {"times": current, "updated_at": now()})
    return overall, per_core


def cpu_temp():
    candidates = []
    for hwmon in Path("/sys/class/hwmon").glob("hwmon*"):
        name = read_text(hwmon / "name")
        if name not in {"coretemp", "k10temp", "zenpower", "thinkpad"}:
            continue
        candidates.extend(
            temp for temp in [read_int(path, 1000) for path in hwmon.glob("temp*_input")] if temp and temp > 0
        )
    return max(candidates) if candidates else None


def cpu_freq():
    current = read_int("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq", 1000)
    maximum = read_int("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", 1000)
    return current, maximum


def top_processes():
    return ps_lines("pcpu", 3)


def tooltip(overall, per_core, temp, freq_current, freq_max):
    lines = [
        f"{span(CPU_ICON, COLORS['red'])} {span('CPU Monitor', COLORS['red'], bold=True)}",
        "─" * 28,
        f"Usage: {span(f'{overall:.0f}%', pct_color(overall), bold=True)}",
    ]
    if temp is not None:
        lines.append(f"Temp:  {span(f'{temp:.0f}°C', temp_color(temp), bold=True)}")
    if freq_current is not None:
        freq_line = f"{freq_current / 1000:.2f} GHz"
        if freq_max:
            freq_line += f" / {freq_max / 1000:.2f} GHz"
        lines.append(f"Clock: {span(freq_line, COLORS['cyan'])}")
    if per_core:
        bars = []
        for usage in per_core[:8]:
            color = pct_color(usage)
            bars.append(span("█", color if usage >= 12 else COLORS["bright_black"]))
        lines.append("")
        lines.append(f"Cores: {''.join(bars)}")

    processes = top_processes()
    if processes:
        lines.extend(["", "Top CPU processes:"])
        for usage, command in processes:
            lines.append(f"• {command[:18]:<18} {span(f'{usage:>4.1f}%', pct_color(usage))}")
    lines.extend(["", "LMB: btop"])
    return "\n".join(lines)


overall, per_core = cpu_usage()
temp = cpu_temp()
freq_current, freq_max = cpu_freq()

text_color = temp_color(temp) if temp is not None else pct_color(overall)
text_value = f"{temp:.0f}°C" if temp is not None else f"{overall:.0f}%"

print_json(
    f"{CPU_ICON} {span(text_value, text_color, bold=True)}",
    tooltip(overall, per_core, temp, freq_current, freq_max),
    "cpu",
)
