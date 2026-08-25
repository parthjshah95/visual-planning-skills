#!/usr/bin/env python3
"""Regenerate the README hero GIF from the example visual plan.

Produces assets/plan-visual.gif — the five-step walkthrough of the animated HTML
plan at skills/visual-plan/examples/csv-export/plan.html. Each frame is captured
with the plan's `?frame=1&scene=N` layout, which fits the header, the animated
flow, and the narration into one clean frame.

Requirements (no Python packages needed):
  - Google Chrome / Chromium (headless screenshots)
  - ImageMagick 7 (`magick`) — assembles the frames into a GIF

Run:  python3 scripts/regenerate-example-gifs.py
"""
import subprocess, os, shutil, tempfile, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN_HTML = REPO / "skills/visual-plan/examples/csv-export/plan.html"
ASSETS = REPO / "assets"
ASSETS.mkdir(exist_ok=True)

def find_chrome():
    mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(mac):
        return mac
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    sys.exit("Could not find Chrome/Chromium. Install it or edit find_chrome().")

CHROME = find_chrome()
MAGICK = shutil.which("magick") or sys.exit("ImageMagick 'magick' not found on PATH.")
WORK = Path(tempfile.mkdtemp(prefix="plan-gif-"))

def shot(scene, out):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", "--virtual-time-budget=1900",
        "--window-size=1200,800", f"--screenshot={out}",
        f"file://{PLAN_HTML}?frame=1&scene={scene}"], check=True)

for i in range(5):
    shot(i, str(WORK / f"h{i}.png"))

subprocess.run([MAGICK, "-loop", "0",
    "-delay", "140", str(WORK / "h0.png"),
    "-delay", "140", str(WORK / "h1.png"),
    "-delay", "150", str(WORK / "h2.png"),
    "-delay", "150", str(WORK / "h3.png"),
    "-delay", "300", str(WORK / "h4.png"),
    "-resize", "1920x", "-layers", "Optimize", str(ASSETS / "plan-visual.gif")], check=True)

shutil.rmtree(WORK, ignore_errors=True)
print("plan-visual.gif", os.path.getsize(ASSETS / "plan-visual.gif"), "bytes")
