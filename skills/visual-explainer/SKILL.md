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

The words carry as much of the explanation as the pictures. Follow these rules for every
human-readable sentence in the output — narration, labels, captions, diagram nodes, glossary
entries:

- **Behavior before mechanism.** Say what the thing does and what the reader observes before you
  name the internal machinery that makes it happen.
- **Define every term before its first use.** If a word is not common English, give a one-line
  definition the first time it appears. Do not carry undefined shorthand forward.
- **Prefer the plain word.** Short common words over formal or rare ones. Spell out an
  abbreviation the first time.
- **Short, active sentences.** One idea per sentence. Prefer the active voice. A good ceiling is
  ~20 words for an instruction and ~25 for a description; split anything longer.
- **One term per concept.** Pick a name and repeat it; do not rotate synonyms for the same thing.

Never apply these rules to code, identifiers, quoted material, or an exact string. Dense
technical shorthand can be accurate and still fail to explain — translate it, don't just drop it
in a glossary and make the reader decode it.

### 3. Pick one concrete example to walk through
Abstract explainers don't land. Choose a single realistic task/ticket/request and follow it
end-to-end through the system. Reuse the *same* example across sections so the reader builds one
mental model. (e.g. one order walked through all the stages of a checkout pipeline.)

### 4. Commit to a visual metaphor + palette
Lean into the subject's own metaphor (a "town" → frontier aesthetic; an SDK/control-plane →
art-deco "city hall" + blueprint cyan; a pipeline → assembly line). Pick a tight palette as CSS
variables and use it everywhere. Distinctive beats generic — avoid the default "AI slop" look
(centered Inter on white cards).

### 5. Build with the standard structure
1. **Header** + a ribbon stating the concrete example (the "ticket").
2. **Cast / concept cards** — one inline-SVG illustration per core concept.
3. **The interactive centerpiece** — pick one:
   - *Scene player*: N scenes, a `data-scene` state machine, narrator panel, prev/next/autoplay.
   - *Pipeline / timeline*: clickable stages with a detail panel + filter chips.
   - *Morph toggle*: cross-fade between two framings (e.g. before/after) via `data-mode`.
4. **Mermaid-style architecture diagram** — hand-built SVG (boxes + arrowhead markers), *not*
   the mermaid.js library (keep it dependency-free).
5. **Glossary** + an "extras / worth knowing" grid.

### 6. Verify before finishing
- Open it mentally: every scene/stage reachable, no actor stuck visible/invisible.
- Grep your own file for broken hex colors and stray placeholder tokens.
- Confirm zero external requests (no `<script src>`, no `<link href>` to CDNs, no web fonts that
  require network — use system font stacks).
- Read every heading, label, caption, and narration as a newcomer: the real-world meaning comes
  before code names, jargon is removed, and every necessary term or abbreviation is defined
  before use.

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
- A concrete narrative thread, not a feature list.

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

## Reference example

[`examples/pipeline-explainer.html`](examples/pipeline-explainer.html) is a complete, working
explainer that demonstrates every pattern above: a morph toggle, a scene player with a narrator
panel, a hand-built mermaid-style architecture diagram, a comparison table, inline-SVG cartoons,
and the safe `renderSegments` core. Copy it as a starting skeleton and replace the content
arrays.
