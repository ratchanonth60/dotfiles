#!/usr/bin/env python3

import argparse
import os
import signal
import sys
import time

DEFAULT_WIDTH = 64
DEFAULT_HEIGHT = 12
DEFAULT_FPS = 30
DEFAULT_DECAY = 0.92
CHARS = [" ", ".", ":", "·", "•", "•"]


def parse_frame(line: str, width: int) -> list[int]:
    try:
        return [int(x) for x in line.strip().split(";") if x][:width]
    except ValueError:
        return [0] * width


def normalize(vals: list[int]) -> list[float]:
    if not vals:
        return []
    low = min(vals)
    high = max(vals)
    scale = high - low
    if scale <= 0:
        return [0.0 for _ in vals]
    return [(v - low) / scale for v in vals]


def get_char_index(val: float) -> int:
    return min(int(val * (len(CHARS) - 1)), len(CHARS) - 1)


def build_frame(history: list[list[float]], height: int, width: int) -> list[str]:
    frame = [[" " for _ in range(width)] for _ in range(height)]

    for x in range(width):
      for y in range(height):
        strength = history[y][x]
        idx = get_char_index(strength)
        frame[height - y - 1][x] = CHARS[idx]

    return ["".join(row) for row in frame]


def run(
    cava_path: str,
    out_path: str,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
    decay: float = DEFAULT_DECAY,
) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    decay_buffer = [[0.0 for _ in range(width)] for _ in range(height)]

    while True:
        try:
            with open(cava_path, "r", encoding="utf-8") as fifo:
                line = fifo.readline()
        except Exception:
            time.sleep(1.0 / fps)
            continue

        if not line:
            time.sleep(1.0 / fps)
            continue

        values = normalize(parse_frame(line, width))
        new_frame = [[0.0 for _ in range(width)] for _ in range(height)]

        for i, val in enumerate(values):
            bar_h = int(val * height)
            for y in range(bar_h):
                new_frame[y][i] = 1.0

        for y in range(height):
            for x in range(width):
                decay_buffer[y][x] = max(decay_buffer[y][x] * decay, new_frame[y][x])

        ascii_lines = build_frame(decay_buffer, height, width)
        with open(out_path, "w", encoding="utf-8") as out:
            out.write("\n".join(ascii_lines))

        time.sleep(1.0 / fps)


def _handle_sigint(signum, frame):
    print("\n[+] CAVA ASCII visualizer stopped.")
    sys.exit(0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CAVA -> ASCII visualizer (compatible with eww/widgets)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--cava-path", default="/tmp/cava.raw")
    parser.add_argument("--out-path", default="/tmp/visualizer.txt")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--decay", type=float, default=DEFAULT_DECAY)

    args = parser.parse_args()
    signal.signal(signal.SIGINT, _handle_sigint)

    run(
        cava_path=args.cava_path,
        out_path=args.out_path,
        width=args.width,
        height=args.height,
        fps=args.fps,
        decay=args.decay,
    )


if __name__ == "__main__":
    main()
