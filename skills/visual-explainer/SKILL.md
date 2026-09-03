---
name: visual-explainer
description: Generate a single-file, interactive HTML explainer for a concept, system, tool, architecture, or workflow — with hand-drawn inline-SVG illustrations, an animated scene-player or pipeline, mermaid-style diagrams, and a glossary. Use when the user asks to illustrate, explain, visualize, or build an interactive walkthrough/explainer of how something works as an HTML page (not a slide deck, not prose).
---

# Visual Explainer — Illustrated, Interactive HTML

Produce a polished, self-contained `.html` file that *teaches how something works* through
illustration and interaction — not by prettifying its docs. The output is one file with no
external dependencies (no CDNs, no build step) that opens in any browser.

This skill encodes a repeatable method and a set of battle-tested code patterns. Follow the
method; reuse the patterns verbatim.

## When to use

- "Create an HTML explainer / illustration of X."
- "Visualize / illustrate how X works, with animations and interactivity."
- "Make an interactive walkthrough of this system/architecture/workflow."

Do **not** use for: static reports (use a doc/pdf/pptx tool), real product UI work (use a
frontend-design skill), or plain prose answers.

## Inputs and custom instructions

```text
/visual-explainer <subject> [instructions=<path>] [out=<dir>]
```

A team's own rules live in a **custom-instructions file**, the same file format the `visual-plan`
skill reads. Pass it with `instructions=<path>`; otherwise a `custom-instructions.md` at the
workspace root is used; otherwise the defaults apply. This skill reads two of its headings:

| Heading | What it holds | Default |
| --- | --- | --- |
| `## Style` | Paths of writing-rule files to read before any human-readable text is written, on top of the always-mandatory `asd-ste100` skill. | None. |
| `## Output` | `Path:` a file path pattern with `<slug>` and `<YYYY-MM-DD>` placeholders. `Publish:` a command or skill to run after the render check passes, with `<file>` as the placeholder. `Report:` what to tell the user after publish. | `<out>/<slug>.html` (default `out` is the current directory); no publish. |

An explicit `out=` argument wins over `Output: Path`. Custom instructions add settings only; they
never change the method below.

## Method (do these in order)

### 1. Research first — never illustrate from memory
The fastest way to ship a *wrong* explainer is to infer the subject. Before drawing anything:
- Pull the real source: fetch the docs, read the actual repo/files, run the tool.
- For doc sites, try `<base>/llms.txt` and `<base>/llms-full.txt` — they often list every page
  and dump full text.
- **Mark confirmed vs inferred.** Anything you couldn't verify is a guess; label it as such in
  the output (e.g. a "modeled, verify" note) rather than asserting it. If a later fetch
  contradicts an earlier claim, fix the explainer — overstating capabilities is the #1 failure
  mode of these explainers.

### 2. Write in plain language before drawing

The words carry as much of the explanation as the pictures.

**Every human-readable string in the output MUST follow the [`asd-ste100`](../asd-ste100/SKILL.md)
skill, strictly.** This covers narration, scene text, captions, diagram labels, decision text, and
glossary entries. It does not cover code, identifiers, or quoted strings. That skill sets the
sentence form: at most 20 words for an instruction and 25 for a description, active voice, simple
tenses, no `-ing` verbs, noun clusters of at most 3 words, one term per concept, and no ellipsis.

Read every file listed under `## Style` in the custom instructions first; it applies on top of
`asd-ste100`. The `asd-ste100` skill governs how to build the sentence. These points govern what to say:

- **Behavior before mechanism.** Say what the thing does, and what the reader sees, before you name
  the machinery.
- **Define every term before its first use.** Give a one-line definition the first time a
  non-common word appears. Do not carry undefined shorthand forward.
- **Translate shorthand.** Dense technical shorthand can be accurate and still fail to explain.
  Translate it. Do not drop it into a glossary and make the reader decode it.

### 3. Pick one concrete example to walk through
Abstract explainers don't land. Choose a single realistic task/ticket/request and follow it
end-to-end through the system. Reuse the *same* example across sections so the reader builds one
mental model. (e.g. one order walked through all the stages of a checkout pipeline.)

### 4. Pick a palette
Pick a tight palette as CSS variables and use it everywhere. Distinctive beats generic: a warm,
cohesive palette reads better than default centered Inter on white cards.

### 5. Build with the standard structure
1. **Header** + a ribbon stating the concrete example (the "ticket").
2. **Concept cards (optional)** — a labeled inline-SVG picture of each part, when seeing the parts helps.
3. **The interactive centerpiece** — pick one:
   - *Scene player*: N scenes, a `data-scene` state machine, narrator panel, prev/next/autoplay.
   - *Pipeline / timeline*: clickable stages with a detail panel + filter chips.
   - *Morph toggle*: cross-fade between two framings (e.g. before/after) via `data-mode`.
4. **Mermaid-style architecture diagram** — hand-built SVG (boxes + arrowhead markers), *not*
   the mermaid.js library (keep it dependency-free).
5. **Glossary** + an "extras / worth knowing" grid.

### 6. Verify before finishing
- **Render it and look at it (required).** Text that spills out of its box and elements that hide
  behind each other are the two defects readers report most. Catch both before the user does:
  1. Paste the whole of [`layout_audit.js`](layout_audit.js) (next to this file) inside a
     `<script>` at the end of `<body>`, and put `data-scenes="N"` on the `[data-scene]` stage.
     The audit runs once at load, steps through every scene, and reports each box whose text
     spills out and each pair of visible boxes that overlap without one containing the other.
  2. Run [`render_check.sh`](render_check.sh)` <file.html>`. It prints the audit lines and
     writes one screenshot per scene (`--size 1400x6000` captures a long page in one image).
     An agent with a browser tool can instead open the file, step with Next, and screenshot.
  3. Open **every** screenshot and read it as the user will: each label fits inside its box,
     nothing hides behind anything, arrows land on their targets, no text runs off the canvas.
  4. Fix each warning and each defect you saw, then rerun. Dismiss a warning only for an
     intended overlap (a badge on a card, a bubble over its speaker) and say so in one line.
  Zero unexplained warnings and a clean look on every screenshot are part of "done".
- Open it mentally: every scene/stage reachable, no actor stuck visible/invisible.
- Grep your own file for broken hex colors and stray placeholder tokens.
- Confirm zero external requests (no `<script src>`, no `<link href>` to CDNs, no web fonts that
  require network — use system font stacks).
- Read every heading, label, caption, and narration as a newcomer: the real-world meaning comes
  before code names, jargon is removed, and every necessary term or abbreviation is defined
  before use.
- Check every human-readable string against the [`asd-ste100`](../asd-ste100/SKILL.md) skill: 20-word
  instructions, 25-word descriptions, active voice, simple tenses, and no `-ing` verbs.

### 7. Deliver

1. Write the file to the `Output: Path` pattern when the custom instructions set one, else to
   `<out>/<slug>.html`.
2. If the custom instructions set `Output: Publish`, run it with the file path substituted for
   `<file>`. If a credential or tool is missing, keep the local file and report each missing
   prerequisite by name.
3. Open the file for the user and print the absolute path. Add the published URL when
   `Output: Report` asks for it.

## Non-negotiable technical patterns

### Avoid `innerHTML` (some harnesses block it; it is safer regardless)
Render dynamic text through DOM nodes only. Storing rich text as arrays of typed segments and
building them with `createElement` sidesteps HTML injection entirely — and some agent harnesses
run a security hook that rejects a `Write` containing `innerHTML`. This exact renderer is the
reusable core:

```js
const ALLOWED_TAGS = new Set(["strong", "em", "code"]);
function renderSegments(target, segments) {
  target.textContent = "";                 // clear
  for (const seg of segments) {
    if (typeof seg === "string") {
      target.appendChild(document.createTextNode(seg));
    } else if (seg && ALLOWED_TAGS.has(seg.tag)) {
      const el = document.createElement(seg.tag);
      el.textContent = String(seg.text ?? "");
      target.appendChild(el);
    }
  }
}
// data:  body: ["Plain ", {tag:"strong", text:"bold"}, " then ", {tag:"code", text:"x()"}]
```

### Single self-contained file
All CSS in one `<style>`, all JS in one `<script>`, all art as inline `<svg>`. No CDNs, no
external fonts, no images. It must work opened directly from disk (`file://`) and offline.

### CSS-driven scene state machine (declarative, animatable)
Put every actor in the SVG once; show/position per scene with attribute selectors. Drive it by
setting one attribute in JS.

```css
.actor { opacity: 0; transition: opacity .5s ease, transform .8s ease; }
.stage[data-scene="3"] .actor-hero { opacity: 1; transform: translateX(120px); }
.stage[data-scene="3"] .speech-3   { opacity: 1; }
```
```js
function setScene(n) {
  stage.setAttribute("data-scene", "0");                 // reset so CSS re-fires
  requestAnimationFrame(() => requestAnimationFrame(() =>  // double rAF = clean re-trigger
    stage.setAttribute("data-scene", String(n))));
}
```

### Responsive SVG
Use `viewBox="0 0 W H"` + `preserveAspectRatio`, size with CSS `width:100%`. Never hardcode px
width on the root SVG.

### Life via CSS keyframes
A few looping animations make it feel alive: `pulse` (heartbeats), `drift` (tumbleweed/clouds),
`smoke`, `flicker` (lanterns/signs), `spin` (gears/loops), `dash` (animated dashed flow lines via
`stroke-dashoffset`).

### Controls + a11y
Prev / Replay / Auto-play / Next, clickable progress dots, and keyboard nav
(`ArrowLeft`/`ArrowRight`/space/`r`). Make clickable cards/dots real `<button>`s or add
`tabindex="0"` + a `keydown` handler.

### Interactivity beyond next/prev
- **Hover tooltips** on diagram parts (`.thing:hover .label { opacity:1 }`).
- **Filter chips** that dim non-matching items (`data-f` + a `matches()` predicate).
- **Morph toggle** (`body[data-mode="..."]`) to cross-fade two states.
- **Clickable detail panel** fed by a JS data array (single source of truth for content).

## Aesthetic checklist

- Distinct theme + palette as `:root` variables; warm, cohesive, intentional.
- Display font for headings, mono for code/labels, serif/system for body (system stacks only).
- Cards: subtle border + offset shadow; hover lift.
- Hand-drawn SVG "cartoons" for concepts — simple flat shapes, recognizable, charming.

## Gotchas (learned the hard way)

- `innerHTML` → the Write may be **rejected by a security hook**, and it is an injection risk
  regardless. Use `renderSegments` above.
- Corrupted/placeholder hex colors silently drop the declaration (e.g. a typo'd
  `#3a4straight`). After writing, grep: `grep -nE '#[0-9a-fA-F]*[g-z]{2,}'` and fix hits.
- Don't ship claims you didn't verify — label modeled/inferred parts explicitly.
- Dense technical shorthand may be accurate and still fail to explain. Translate it into plain
  language instead of putting the shorthand in a glossary and making the reader decode it.
- Keep it one file; resist pulling in chart/diagram libraries.
- Test the very first and very last scene — off-by-one in the `data-scene` map is common.
- Long labels in a fixed-width box are the top overflow cause. Wrap with `<tspan>` lines or a
  `<foreignObject>`, or widen the box; never shrink the font below 11 px to make it fit.

## Files in this skill

- [`layout_audit.js`](layout_audit.js) — inline load-time audit: text overflow and box overlap, per scene. Findings go to the console and a hidden `<pre id="layout-audit">`; `?audit=show` displays it; `#scene=N` opens scene N.
- [`render_check.sh`](render_check.sh) — headless Chrome runner: prints the audit lines, writes one PNG per scene, exits 2 when any warning remains.
- [`test_layout_audit.sh`](test_layout_audit.sh) — fixture self-check. Run `bash skills/visual-explainer/test_layout_audit.sh`.

## Reference example

[`examples/pipeline-explainer.html`](examples/pipeline-explainer.html) is a complete, working
explainer that demonstrates every pattern above: a morph toggle, a scene player with a narrator
panel, a hand-built mermaid-style architecture diagram, a comparison table, inline-SVG cartoons,
and the safe `renderSegments` core. Copy it as a starting skeleton and replace the content
arrays.
