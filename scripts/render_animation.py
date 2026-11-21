#!/usr/bin/env python3
"""Render a schematic GIF and MP4 from the checked-in synthetic HyTwin traces.

Optional dependencies: requirements-media.txt. No plant connection is made.
All tank levels are interpolated from results/demo/traces.csv, not invented
by the animation. Video time includes a paused introduction and conclusion.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 800
FPS, INTRO, RUN, OUTRO = 15, 4, 20, 6
TOTAL = INTRO + RUN + OUTRO
BG = "#0b1423"
CARD = "#111f32"
LINE = "#34465f"
WHITE = "#edf4ff"
MUTED = "#aabbd1"
TEAL = "#5cddc2"
RED = "#ff7f8a"
AMBER = "#ffcb77"
WATER = "#2778a9"


def font_path(bold: bool) -> Path:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / name
    if not path.exists():
        raise SystemExit("Install DejaVu Sans fonts (Debian/Ubuntu: fonts-dejavu-core)")
    return path


FONTS = {}


def text(draw, xy, value, size=16, fill=WHITE, bold=False, anchor=None):
    key = size, bold
    if key not in FONTS:
        FONTS[key] = ImageFont.truetype(str(font_path(bold)), size)
    draw.text(xy, value, font=FONTS[key], fill=fill, anchor=anchor)


def pill(draw, box, value, color, size=12):
    draw.rounded_rectangle(box, radius=9, fill=color)
    text(draw, ((box[0]+box[2])/2, (box[1]+box[3])/2), value,
         size=size, fill=BG, bold=True, anchor="mm")


def load_evidence():
    summary = json.loads((ROOT / "results/demo/summary.json").read_text())
    names = ["transfer-unmitigated", "transfer-mitigated", "transfer-late"]
    cases = {case["name"]: case for case in summary["scenarios"] if case["name"] in names}
    samples = {name: {} for name in names}
    with (ROOT / "results/demo/traces.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            if row["scenario"] in samples:
                # The final entry at a scan timestamp contains the new commands.
                samples[row["scenario"]][float(row["time_s"])] = row
    for name, case in cases.items():
        rows = sorted(samples[name].items())
        case["samples"] = rows
        case["times"] = [time for time, _ in rows]
        case["deadline"] = case["attack_started_at_s"] + case["held_command_horizon_at_attack_s"]
    return summary["parameters"], [cases[name] for name in names]


def sample(case, time):
    rows = case["samples"]
    index = max(0, min(len(rows)-1, bisect_right(case["times"], time)-1))
    stamp, row = rows[index]
    result = {key: float(row[key]) for key in ("x1", "x2", "v1", "v2", "p2")}
    if index + 1 < len(rows):
        next_stamp, next_row = rows[index+1]
        ratio = max(0.0, min(1.0, (time-stamp)/(next_stamp-stamp)))
        for key in ("x1", "x2"):
            result[key] += (float(next_row[key])-result[key])*ratio
    return result


def tank(draw, x, top, bottom, width, level, time, color, threshold=None):
    """Schematic level geometry; neither physical dimensions nor a spill model."""
    maximum = 14.0
    water_y = bottom - (bottom-top-4)*min(maximum, max(0, level))/maximum
    if water_y < bottom-3:
        points = [(x+3, bottom-3), (x+3, water_y)]
        for offset in range(0, width-5, 3):
            points.append((x+3+offset, water_y + 1.5*math.sin(offset/12+time*3)))
        points.extend([(x+width-3, water_y), (x+width-3, bottom-3)])
        draw.polygon(points, fill=color)
        for offset in range(12, width-8, 22):
            draw.line((x+offset, bottom-12, x+offset+8, bottom-12), fill="#417e9f", width=1)
    draw.line((x, top, x, bottom, x+width, bottom, x+width, top), fill="#abc3d9", width=3)
    draw.line((x-4, top, x+5, top), fill="#abc3d9", width=3)
    draw.line((x+width-5, top, x+width+4, top), fill="#abc3d9", width=3)
    if threshold is not None:
        y = bottom - (bottom-top-4)*threshold/maximum
        for start in range(int(x-9), int(x+width+10), 12):
            draw.line((start, y, start+6, y), fill=WHITE, width=2)
        text(draw, (x+width-2, y-17), "HH = 12", size=11, bold=True, anchor="ra")


def flow(draw, x0, x1, y, moving, time, color):
    draw.line((x0, y, x1, y), fill=LINE, width=12)
    draw.line((x0, y, x1, y), fill="#25465d", width=5)
    if moving:
        for base in range(int(x0), int(x1), 24):
            x = x0 + (base-x0 + time*28) % (x1-x0)
            draw.polygon([(x-4, y-4), (x+3, y), (x-4, y+4)], fill=color)


def case_panel(draw, left, index, case, params, time):
    width = 360
    row = sample(case, time)
    started = time >= case["attack_started_at_s"]
    stopped = case["intervention_at_s"] is not None and time >= case["intervention_at_s"]
    violated = row["x2"] > params["upper"]+1e-8
    at_boundary = abs(row["x2"]-params["upper"]) <= 1e-8
    accent = [RED, TEAL, AMBER][index]
    status_color = RED if violated else TEAL if stopped else AMBER if started else MUTED
    title = ["No intervention", "Timely intervention", "Delayed intervention"][index]
    response = ["Response: none", "Response delay: 2 s", "Response delay: 16 s"][index]
    draw.rounded_rectangle((left, 219, left+width, 592), radius=15, fill=CARD,
                           outline=accent if violated or stopped else LINE, width=2)
    text(draw, (left+20, 236), title, size=22, bold=True, fill=accent)
    text(draw, (left+20, 267), response, size=14, fill=MUTED)
    status = ("UNSAFE LEVEL" if violated else "SAFE SHUTDOWN" if stopped else
              "BOUNDARY REACHED" if at_boundary else "ATTACK ACTIVE" if started else "NORMAL CONTROL")
    pill(draw, (left+20, 294, left+width-20, 320), status, status_color, size=11)

    sx, rx, bottom = left+23, left+221, 519
    inlet_color = TEAL if row["v1"] else MUTED
    text(draw, (left+17, 338), "RAW INLET", size=9, fill=inlet_color)
    draw.line((left+13,355,left+13,405,sx+2,405),fill=LINE,width=7)
    if row["v1"]:
        draw.line((left+13,355,left+13,405,sx+2,405),fill="#2778a9",width=3)
        draw.polygon([(sx-6,401),(sx+1,405),(sx-6,409)],fill=TEAL)
        dot_y = 357+(time*24)%42
        draw.ellipse((left+11,dot_y-2,left+15,dot_y+2),fill=TEAL)
    else:
        draw.line((left+7,366,left+19,374),fill=MUTED,width=2)
    text(draw, (sx+40, 365), "Source tank", size=12, fill=MUTED, anchor="mm")
    text(draw, (rx+57, 341), "Process tank", size=12, fill=MUTED, anchor="mm")
    flow(draw, sx+80, rx, 451, bool(row["p2"] and row["v2"]), time, accent)
    tank(draw, sx, 382, bottom, 80, row["x1"], time, WATER)
    tank(draw, rx, 354, bottom, 114, row["x2"], time,
         "#a44154" if violated else "#237f79" if stopped else WATER, threshold=params["upper"])

    # Pump and valve use the actual recorded actuator commands.
    pcx, pcy = left+151, 451
    pump_color = accent if row["p2"] else MUTED
    draw.ellipse((pcx-20,pcy-20,pcx+20,pcy+20), fill=BG, outline=pump_color, width=3)
    angle = time*6 if row["p2"] else 0
    for blade in range(3):
        a = angle+blade*math.tau/3
        draw.line((pcx,pcy,pcx+13*math.cos(a),pcy+13*math.sin(a)), fill=pump_color, width=3)
    vx = left+195
    valve_color = accent if row["v2"] else MUTED
    draw.polygon([(vx-8,443),(vx+8,459),(vx+8,443),(vx-8,459)], fill=BG, outline=valve_color, width=2)
    if not row["v2"]:
        draw.line((vx-9,461,vx+9,441), fill=valve_color, width=2)
    text(draw, (pcx, 481), "PUMP " + ("ON" if row["p2"] else "OFF"), size=10, fill=pump_color, anchor="mm")
    text(draw, (vx, 420), "VALVE", size=9, fill=valve_color, anchor="mm")
    text(draw, (sx+40, 536), f'x1 = {row["x1"]:.2f}', size=13, anchor="mm")
    text(draw, (rx+57, 536), f'x2 = {row["x2"]:.2f}', size=16, bold=True, anchor="mm")
    if violated:
        tx, ty = rx+57, 438
        draw.polygon([(tx,ty-22),(tx-21,ty+17),(tx+21,ty+17)], fill=AMBER)
        text(draw,(tx,ty+2),"!",size=24,fill=BG,bold=True,anchor="mm")
        note = "Unsafe level: overflow risk"
    elif stopped:
        note = "Flow stopped; safe level maintained"
    elif started:
        note = f'Safety margin: {max(0,case["deadline"]-time):.1f} s remaining'
    else:
        note = "Physical state starts inside safe limits"
    text(draw, (left+width/2, 568), note, size=12, fill=status_color, bold=True, anchor="mm")


def render_frame(video_time, params, cases):
    time = max(0.0, min(RUN, video_time-INTRO))
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    text(draw, (36, 25), "HYTWIN  /  NFM 2025", size=15, fill=TEAL, bold=True)
    pill(draw, (872, 22, 1164, 51), "ILLUSTRATIVE SYNTHETIC SIMULATION", MUTED, size=11)
    text(draw, (36, 65), "When a cyberattack reaches the plant", size=37, bold=True)
    text(draw, (36, 116), "One actuator attack. Three response strategies. Different physical safety outcomes.", size=18, fill=MUTED)
    draw.rounded_rectangle((36,155,1164,195), radius=9, fill="#1c2d43")
    if video_time < INTRO:
        banner = "THE SCENARIO   /   An attacker forces a transfer pump and valve open."
    elif time < 2:
        banner = "NORMAL OPERATION   /   The process starts inside its safety limits."
    elif time <= 17:
        banner = "ATTACK ACTIVE   /   Continued transfer raises the receiving tank level."
    else:
        banner = "PHYSICAL CONSEQUENCE   /   Exceeding the upper bound creates an overflow risk."
    text(draw, (56, 166), banner, size=16, bold=True)
    for index, case in enumerate(cases):
        case_panel(draw, 36+index*384, index, case, params, time)

    text(draw, (48, 616), f"SIMULATION TIME   {time:05.2f} s", size=15, bold=True)
    text(draw, (1152, 616), "Closed safety bound: x2 <= HH = 12", size=13, fill=MUTED, anchor="ra")
    x0, x1, y = 60, 1140, 655
    draw.rounded_rectangle((x0,y,x1,y+6), radius=3, fill=LINE)
    draw.rounded_rectangle((x0,y,x0+(x1-x0)*time/RUN+1,y+6), radius=3, fill=TEAL)
    for tick in (0,5,10,15,20):
        x = x0+(x1-x0)*tick/RUN
        draw.line((x,y+8,x,y+13), fill=MUTED, width=1)
        text(draw,(x,y+22),f"{tick} s",size=11,fill=MUTED,anchor="mm")
    for stamp, label, color in ((2,"Attack",AMBER),(17,"Safety boundary",RED)):
        x = x0+(x1-x0)*stamp/RUN
        draw.line((x,y-10,x,y+7),fill=color,width=2)
        text(draw,(x,y-20),label,size=11,fill=color,anchor="mm")

    if video_time < INTRO:
        caption = "A compromised PLC command can become a physical safety hazard."
    elif video_time >= INTRO+RUN:
        caption = "Detecting the attack is only the start. Acting in time protects physical safety."
    elif time < 2:
        caption = "The experiment begins with all tank levels inside the safe range."
    elif time < 4:
        caption = "Attack at t = 2 s. This fixed-flow scenario has a 15 s intervention window."
    elif time < 17:
        caption = "Timely shutdown stops transfer. Waiting consumes the remaining safety margin."
    elif time <= 17+1e-8:
        caption = "The upper boundary is reached. Continuing to fill would violate safety."
    elif time < 18:
        caption = "The safety limit is exceeded before the delayed intervention takes effect."
    else:
        caption = "Late shutdown stops the flow, but it cannot undo the safety violation."
    draw.rounded_rectangle((36,708,1164,761),radius=9,fill="#1c2d43")
    text(draw,(600,734),caption,size=17,fill=WHITE,bold=True,anchor="mm")
    text(draw,(600,782),"Schematic geometry; chosen level units; synthetic model traces. Clock pauses for introduction and conclusion.",
         size=11,fill=MUTED,anchor="mm")
    return image


def run(command):
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"assets/media")
    parser.add_argument("--qa-dir",type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    params,cases = load_evidence()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    video = args.output/"hytwin-impact.mp4"
    gif = args.output/"hytwin-impact.gif"
    poster = args.output/"hytwin-impact-poster.png"
    with tempfile.TemporaryDirectory(prefix="hytwin-animation-") as folder:
        folder = Path(folder)
        for index in range(FPS*TOTAL):
            frame=render_frame(index/FPS,params,cases)
            frame.save(folder/f"frame-{index:04d}.png",compress_level=1)
        run([ffmpeg,"-hide_banner","-loglevel","error","-y","-framerate",str(FPS),
             "-i",str(folder/"frame-%04d.png"),"-c:v","libx264","-crf","21",
             "-pix_fmt","yuv420p","-movflags","+faststart",str(video)])
        # Generate the GIF directly from lossless frames, avoiding video artifacts.
        run([ffmpeg,"-hide_banner","-loglevel","error","-y","-framerate",str(FPS),
             "-i",str(folder/"frame-%04d.png"),"-filter_complex",
             "fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=none",
             "-loop","0",str(gif)])
    render_frame(26,params,cases).save(poster)
    if args.qa_dir:
        args.qa_dir.mkdir(parents=True,exist_ok=True)
        for stamp in (0,6,8,20,21,21.1,22,26,29):
            render_frame(stamp,params,cases).save(args.qa_dir/f"video-{stamp:g}s.png")
    manifest = {
        "artifact_type":"illustrative animation from checked-in synthetic traces",
        "video_duration_s":TOTAL,"video_fps":FPS,"video_size":[WIDTH,HEIGHT],
        "gif_fps":10,"gif_size":[960,640],"simulation_interval_s":[0,RUN],
        "intro_hold_s":INTRO,"outro_hold_s":OUTRO,"audio":"none; on-screen captions",
        "case_names":[case["name"] for case in cases],
        "interpolation":"piecewise linear physical levels; sampled actuator states",
        "scope":"Schematic physical safety consequences; no measured spill volume, deployed guarantee, or detector latency claim",
        "pillow_version":pillow_version,"imageio_ffmpeg_version":imageio_ffmpeg.__version__,
        "encoder_version":subprocess.check_output([ffmpeg,"-version"],text=True).splitlines()[0],
        "width":WIDTH,"height":HEIGHT,"mp4_frames_per_second":FPS,"duration_seconds":TOTAL,
        "sources_sha256":{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (ROOT/"results/demo/traces.csv",ROOT/"results/demo/summary.json",Path(__file__))},
        "fonts_sha256":{font_path(bold).name:hashlib.sha256(font_path(bold).read_bytes()).hexdigest() for bold in (False,True)},
        "files_sha256":{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in (gif,video,poster)},
        "files_bytes":{path.name:path.stat().st_size for path in (gif,video,poster)},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest["files_bytes"],indent=2))
    print(f"Created {TOTAL} s animation in {args.output}")


if __name__ == "__main__":
    main()
