#!/usr/bin/env python3

import os
from pathlib import Path

from monitor_suite import COLORS, lspci_name, print_json, read_int, read_text, runtime_status, span, temp_color

GPU_ICON = "󰢮"
VENDORS = {
    "0x8086": "Intel",
    "0x10de": "NVIDIA",
    "0x1002": "AMD",
}


def gpu_entries():
    entries = []
    for card in sorted(Path("/sys/class/drm").glob("card[0-9]")):
        device = card / "device"
        vendor_id = read_text(device / "vendor")
        if not vendor_id:
            continue
        vendor = VENDORS.get(vendor_id.lower(), vendor_id)
        slot = os.path.basename(os.path.realpath(device))
        driver = Path(os.path.realpath(device / "driver")).name if (device / "driver").exists() else "unknown"
        temps = []
        for hwmon in (device / "hwmon").glob("hwmon*"):
            temps.extend(
                temp for temp in [read_int(path, 1000) for path in hwmon.glob("temp*_input")] if temp and temp > 0
            )
        temperature = max(temps) if temps else None
        status = runtime_status(device)
        name = lspci_name(slot, f"{vendor} GPU")
        entries.append(
            {
                "card": card.name,
                "name": name,
                "vendor": vendor,
                "driver": driver,
                "slot": slot,
                "temperature": temperature,
                "status": status,
            }
        )
    return entries


def tooltip(entries):
    lines = [
        f"{span(GPU_ICON, COLORS['magenta'])} {span('GPU Monitor', COLORS['magenta'], bold=True)}",
        "─" * 34,
    ]
    if not entries:
        lines.append("No GPU telemetry was detected.")
        return "\n".join(lines)

    for entry in entries:
        lines.append(span(entry["name"], COLORS["white"], bold=True))
        lines.append(f"• Card:   {entry['card']} ({entry['vendor']})")
        lines.append(f"• Driver: {entry['driver']}")
        lines.append(f"• Power:  {entry['status']}")
        if entry["temperature"] is not None:
            lines.append(f"• Temp:   {span(f'{entry['temperature']:.0f}°C', temp_color(entry['temperature']))}")
        else:
            lines.append(f"• Temp:   {span('N/A', COLORS['bright_black'])}")
        lines.append("")
    lines.append("LMB: btop")
    return "\n".join(lines)


entries = gpu_entries()
hottest = max((entry["temperature"] for entry in entries if entry["temperature"] is not None), default=None)
text = "N/A" if hottest is None else f"{hottest:.0f}°C"
color = COLORS["bright_black"] if hottest is None else temp_color(hottest)

print_json(
    f"{GPU_ICON} {span(text, color, bold=True)}",
    tooltip(entries),
    "gpu",
)
