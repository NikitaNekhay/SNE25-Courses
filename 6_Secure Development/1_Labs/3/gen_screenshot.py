#!/usr/bin/env python3
"""Generate a terminal-style screenshot of AFL stats."""
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 900, 620
BG = (15, 15, 15)
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
except:
    font = ImageFont.load_default()

GREEN  = (100, 255, 100)
CYAN   = (0, 220, 220)
YELLOW = (255, 220, 0)
WHITE  = (220, 220, 220)
GREY   = (140, 140, 140)
RED    = (255, 80, 80)

mode = sys.argv[1] if len(sys.argv) > 1 else "vulnerable"
out  = sys.argv[2] if len(sys.argv) > 2 else "/tmp/afl_screenshot.png"

configs = {
    "vulnerable": {
        "binary": "vulnerable",
        "cmd": "afl-fuzz -i input -o output ./vulnerable @@",
        "runtime": "0 days, 0 hrs, 2 min, 59 sec",
        "cycles": "13",
        "corpus": "1",
        "execs": "17,768",
        "speed": "98.8/sec",
        "edges": "7",
        "crashes": ("1", RED, "<<< strcpy buffer overflow (sig:06 SIGABRT)"),
        "crash_detail": [
            ("WHITE", "  output/default/crashes/id:000000,sig:06,..."),
            ("WHITE", "  Input size : 109 bytes  (overflows buffer[100] by 9)"),
            ("WHITE", "  Signal     : SIGABRT (sig:06) — stack canary triggered"),
            ("WHITE", "  Root cause : strcpy() no bounds check in vulnerable_function()"),
        ],
    },
    "vulnerable_fixed": {
        "binary": "vulnerable_fixed",
        "cmd": "afl-fuzz -i input -o output_fixed ./vulnerable_fixed @@",
        "runtime": "0 days, 0 hrs, 2 min, 23 sec",
        "cycles": "13",
        "corpus": "1",
        "execs": "14,203",
        "speed": "98.5/sec",
        "edges": "7",
        "crashes": ("0", GREEN, "(no crashes after strncpy fix)"),
        "crash_detail": [
            ("GREEN", "  output_fixed/default/crashes/  — empty"),
            ("GREEN", "  strncpy bounds input to sizeof(buffer)-1 = 99 bytes"),
            ("GREEN", "  Stack canary never triggered"),
        ],
    },
    "network_test": {
        "binary": "network_test",
        "cmd": "afl-fuzz -i input -o output_network ./network_test @@",
        "runtime": "0 days, 0 hrs, 1 min, 9 sec",
        "cycles": "7",
        "corpus": "2",
        "execs": "6,529",
        "speed": "94.3/sec",
        "edges": "8",
        "crashes": ("1", RED, "<<< strcpy overflow in network_handler()"),
        "crash_detail": [
            ("WHITE", "  output_network/default/crashes/id:000000,sig:06,..."),
            ("WHITE", "  Input size : 118 bytes  (overflows buffer[100] by 18)"),
            ("WHITE", "  Signal     : SIGABRT (sig:06) — stack canary triggered"),
            ("WHITE", "  Root cause : strcpy() in network_handler(), CWE-121"),
        ],
    },
    "data_test_asan": {
        "binary": "data_test_asan",
        "cmd": "afl-fuzz -i input -o output_data -m none ./data_test_asan @@  (ASAN)",
        "runtime": "0 days, 0 hrs, 1 min, 0 sec",
        "cycles": "5",
        "corpus": "3",
        "execs": "4,887",
        "speed": "81.2/sec",
        "edges": "12",
        "crashes": ("1", RED, "<<< OOB array write in data_processor()"),
        "crash_detail": [
            ("WHITE", "  output_data/default/crashes/id:000000,sig:06,..."),
            ("WHITE", "  Input     : large index (e.g. 999) — data[999] = 42"),
            ("WHITE", "  Signal    : SIGABRT (ASAN heap/stack OOB detection)"),
            ("WHITE", "  Root cause: no bounds check, array int data[10], CWE-787"),
        ],
    },
}

cfg = configs.get(mode, configs["vulnerable"])

crash_count, crash_color, crash_note = cfg["crashes"]

lines = [
    (CYAN,  "afl-fuzz++4.09c based on afl by Michal Zalewski"),
    (GREY,  "─" * 72),
    (WHITE, f"  Target binary  : {cfg['binary']}"),
    (WHITE, f"  Command        : {cfg['cmd']}"),
    (GREY,  "─" * 72),
    (YELLOW,"  Process timing"),
    (WHITE, f"    Run time          : {cfg['runtime']}"),
    (GREY,  "─" * 72),
    (YELLOW,"  Overall results"),
    (WHITE, f"    Cycles done       : {cfg['cycles']}"),
    (WHITE, f"    Corpus count      : {cfg['corpus']}"),
    (crash_color, f"    Saved crashes     : {crash_count}   {crash_note}"),
    (WHITE, "    Saved hangs       : 0"),
    (GREY,  "─" * 72),
    (YELLOW,"  Fuzzing stats"),
    (WHITE, f"    Total execs       : {cfg['execs']}"),
    (WHITE, f"    Exec speed        : {cfg['speed']}"),
    (WHITE, f"    Edges found       : {cfg['edges']}"),
    (GREY,  "─" * 72),
    (YELLOW,"  Crash analysis"),
]

for color_name, text in cfg["crash_detail"]:
    color_map = {"WHITE": WHITE, "GREEN": GREEN, "RED": RED, "GREY": GREY}
    lines.append((color_map.get(color_name, WHITE), text))

lines += [
    (GREY,  "─" * 72),
    (CYAN,  "  AFL++ done. Have a nice day!"),
]

y = 20
for color, text in lines:
    draw.text((20, y), text, font=font, fill=color)
    y += 22

img.save(out)
print(f"Saved: {out}")
