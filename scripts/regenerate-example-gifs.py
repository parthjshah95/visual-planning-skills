#!/usr/bin/env python3
"""Regenerate the README comparison GIFs from the example plans.

Produces:
  assets/plan-markdown.gif  — a slow scroll through the rendered Markdown plan
  assets/plan-visual.gif    — the 5-step walkthrough of the animated HTML plan

Requirements (no Python packages needed):
  - Google Chrome / Chromium (headless screenshots)
  - ImageMagick 7 (`magick`) — assembles the frames into GIFs

Both example plans are the same feature — "Add CSV export to the Reports page" —
under skills/visual-plan/examples/csv-export/. Edit those, then run this to refresh
the GIFs:  python3 scripts/regenerate-example-gifs.py
"""
import subprocess, os, struct, shutil, tempfile, re, html, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "skills/visual-plan/examples/csv-export"
PLAN_HTML = EXAMPLE / "plan.html"
PLAN_MD = EXAMPLE / "plan.md"
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
WORK = Path(tempfile.mkdtemp(prefix="plan-gifs-"))

def run(cmd): subprocess.run(cmd, check=True)
def shot(url, out, w, h, budget=1900, scale=2):
    run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         f"--force-device-scale-factor={scale}", f"--virtual-time-budget={budget}",
         f"--window-size={w},{h}", f"--screenshot={out}", url])
def png_size(p):
    d = open(p, "rb").read(33); return struct.unpack(">II", d[16:24])

# ---------- render the Markdown plan to a light, GitHub-style page ----------
def md_inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t

def md_block_start(ln):
    return ln.startswith("#") or ln.startswith("- ") or re.match(r"^\d+\. ", ln) or not ln.strip()

def md_cont(lines, i):
    buf = []
    while i < len(lines) and lines[i].strip() and lines[i][0] in " \t":
        buf.append(lines[i].strip()); i += 1
    return buf, i

def md_to_html(md):
    lines, out, i = md.split("\n"), [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1; continue
        if ln.startswith("### "): out.append(f"<h3>{md_inline(ln[4:])}</h3>"); i += 1
        elif ln.startswith("## "): out.append(f"<h2>{md_inline(ln[3:])}</h2>"); i += 1
        elif ln.startswith("# "): out.append(f"<h1>{md_inline(ln[2:])}</h1>"); i += 1
        elif re.match(r"^- \[[ xX]\] ", ln):
            items = []
            while i < len(lines) and re.match(r"^- \[[ xX]\] ", lines[i]):
                checked, txt = lines[i][3] in "xX", lines[i][6:]
                cont, i = md_cont(lines, i + 1)
                if cont: txt += " " + " ".join(cont)
                box = "&#9745;" if checked else "&#9744;"
                items.append(f'<li class="task">{box} {md_inline(txt)}</li>')
            out.append('<ul class="tasks">' + "".join(items) + "</ul>")
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                txt = lines[i][2:]; cont, i = md_cont(lines, i + 1)
                if cont: txt += " " + " ".join(cont)
                items.append(f"<li>{md_inline(txt)}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
        elif re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                txt = re.sub(r"^\d+\. ", "", lines[i]); cont, i = md_cont(lines, i + 1)
                if cont: txt += " " + " ".join(cont)
                items.append(f"<li>{md_inline(txt)}</li>")
            out.append("<ol>" + "".join(items) + "</ol>")
        else:
            para = [ln.strip()]; i += 1
            while i < len(lines) and lines[i].strip() and not md_block_start(lines[i]):
                para.append(lines[i].strip()); i += 1
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
    return "\n".join(out)

md_render = WORK / "md-render.html"
md_render.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{{margin:0;background:#fff;}}
  .doc{{max-width:820px;margin:0 auto;padding:44px 52px 60px;
    font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#1f2328;}}
  h1{{font-size:30px;border-bottom:1px solid #d1d9e0;padding-bottom:.3em;margin:0 0 16px;}}
  h2{{font-size:21px;border-bottom:1px solid #d1d9e0;padding-bottom:.3em;margin:30px 0 12px;}}
  h3{{font-size:17px;margin:22px 0 8px;}}
  p{{margin:.7em 0;}} strong{{font-weight:640;}}
  code{{background:#eff1f3;padding:.16em .4em;border-radius:6px;
    font:13px "SFMono-Regular",Consolas,Menlo,monospace;}}
  ul,ol{{padding-left:1.7em;margin:.5em 0;}} li{{margin:.3em 0;}}
  ul.tasks{{list-style:none;padding-left:.2em;}} li.task{{color:#59636e;}}
</style></head><body><div class="doc">{md_to_html(PLAN_MD.read_text())}</div></body></html>""")

# ---------- 1. visual plan: 5-step walkthrough ----------
for i in range(5):
    shot(f"file://{PLAN_HTML}?frame=1&scene={i}", str(WORK / f"h{i}.png"), 1200, 800)
run([MAGICK, "-loop", "0",
     "-delay", "140", str(WORK / "h0.png"),
     "-delay", "140", str(WORK / "h1.png"),
     "-delay", "150", str(WORK / "h2.png"),
     "-delay", "150", str(WORK / "h3.png"),
     "-delay", "300", str(WORK / "h4.png"),
     "-resize", "960x", "-layers", "Optimize", str(ASSETS / "plan-visual.gif")])

# ---------- 2. markdown plan: slow scroll ----------
shot(f"file://{md_render}", str(WORK / "md-tall.png"), 1000, 7000, budget=1500)
run([MAGICK, str(WORK / "md-tall.png"), "-trim", "+repage", str(WORK / "md-trim.png")])
W, H = png_size(str(WORK / "md-trim.png"))
win_h, n = 1400, 26
max_off = max(0, H - win_h)
frames = []
for k in range(n):
    off = round(max_off * k / (n - 1)) if n > 1 else 0
    fp = WORK / f"md_{k:03d}.png"
    run([MAGICK, str(WORK / "md-trim.png"), "-crop", f"{W}x{win_h}+0+{off}", "+repage", str(fp)])
    frames.append(fp)
args = [MAGICK, "-loop", "0"]
for k, fp in enumerate(frames):
    args += ["-delay", "170" if k in (0, len(frames) - 1) else "13", str(fp)]
args += ["-resize", "860x", "-colors", "96", "-layers", "Optimize", str(ASSETS / "plan-markdown.gif")]
run(args)

shutil.rmtree(WORK, ignore_errors=True)
for g in ("plan-visual.gif", "plan-markdown.gif"):
    print(g, os.path.getsize(ASSETS / g), "bytes")
