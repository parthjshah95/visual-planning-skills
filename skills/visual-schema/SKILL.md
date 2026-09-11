---
name: visual-schema
description: Generate a single-file, interactive HTML diagram of a database schema — entity boxes with typed fields, colored domain groups, relationship edges with a legend, and click-to-focus highlighting. The tables come from the real model source (ORM models, migrations, or DDL), never from memory. Use when the user asks to visualize, diagram, or document a database schema, data model, or table structure as an HTML page.
---

# Visual Schema — Interactive Database Diagrams

Produce one self-contained `.html` file that shows a database schema: every table as an entity box, fields with types and badges, tables clustered into colored domain groups, and relationships drawn as labeled edges. No CDN, no build step. The file opens offline, from disk.

The output is a **living document**. Teams edit it every time the schema changes. Most rules in this skill exist so those edits stay safe.

## When to use

- "Visualize / diagram this database schema as an HTML page."
- "Document the data model with an entity diagram."
- "Add the new tables to the schema diagram."

Do **not** use for: one-off architecture sketches (use `visual-explainer`) or prose data dictionaries. To author a schema-change plan, use `visual-plan`. That skill embeds this skill's **change mode** (below) for the plan's schema section.

## Method (do these in order)

### 1. Extract from the real source — never invent

Read the actual model source: ORM model classes, migrations, or SQL DDL. For every table record:

- The table name, and whether it is abstract (a shared base with no table).
- Every field: name, type, nullable, default, unique, primary key.
- Every foreign key and inheritance edge.

A diagram with an invented field is worse than no diagram. If the source is ambiguous, ask.

### 2. Group tables by domain

Cluster tables into 2–6 named groups (identity, catalog, billing, …). A group gets a short label and a one-line caption. Every table belongs to exactly one group.

### 3. Author the data, not the drawing

The file's single source of truth is three JS arrays. All rendering derives from them.

```js
const GROUPS = {
  identity: { label: "Identity", caption: "Who is acting", color: "#46b8d8" },
  // NO x, y, width, or height here — group geometry is DERIVED (see rule 3 below)
};

const TABLES = [
  {
    id: "user",                 // stable id, used by RELATIONSHIPS
    group: "identity",
    title: "User",
    tag: "table",               // or "abstract · no table"
    x: 80, y: 120,              // hand-placed position — the ONLY hand geometry
    width: 320,
    fields: [
      { name: "id",         badges: "●", type: "ULID" },
      { name: "email",      badges: "◆", type: "text" },
      { name: "deleted_at", badges: "°", type: "timestamptz" },
    ],
    note: "",                   // see rule 1 below
  },
];

const RELATIONSHIPS = [
  { from: "session", to: "user", label: "belongs to", kind: "fk" },
  { from: "user", to: "base_model", label: "inherits timestamps and soft delete", kind: "inherit" },
];
```

Badge vocabulary — use these and only these, and show them in the legend:

| Badge | Meaning |
| --- | --- |
| `●` | primary key |
| `◆` | unique |
| `°` | nullable |

Foreign keys are edges, not badges. Edge `kind` values get distinct dash patterns (`fk` solid, `inherit` dashed, others as needed), each shown in the legend.

## Three load-bearing rules

These rules exist because each one failed in practice in maintained diagrams. They are not style preferences.

### Rule 1 — notes are capped at 30 words

A table `note` is optional and **at most 30 words**. Prefer an empty note. A note states one constraint the fields cannot show ("Audits changed field names only."). A note never summarizes the fields, never explains the domain, and never carries a paragraph. If a table seems to need more, the words belong in the repo's docs, not in the diagram.

### Rule 2 — a grown table forces a re-layout

A table's height is **computed from its field count** — never hardcoded. So when an edit adds fields, the table gets taller, and when an edit adds a table, the canvas gets fuller. After **every** edit that adds a table or a field:

1. Recompute the layout. Move neighbors down or aside so that **no table overlaps another** and every gap is at least 24 px.
2. Never "fit" a grown table by clipping it, shrinking it, or letting it slide behind a neighbor.
3. Run the built-in layout audit (below) and fix every warning before you finish.

### Rule 3 — group regions and the canvas are derived, never hand-sized

A group's colored rectangle is **computed** from the bounding box of its member tables plus padding. The canvas size is **computed** from the union of the group rectangles plus a margin. Neither is ever a hardcoded number. This makes the "table outgrew its colored section" failure impossible: when a member grows or a table joins, the region and the canvas grow with it.

When you maintain an older diagram that hand-codes group `x/y/width/height` or a `CANVAS_HEIGHT`: resize those numbers **in the same edit** that grows a table — or better, convert them to derived values while you are there.

## Change mode (optional)

Use change mode for a schema-change view, not the whole database. The `visual-plan` skill embeds this mode for a schema-change plan. Change mode adds a table change state, a field change state, and a context table.

A **context table** is a table the change does not touch. The diagram shows it only so an edge has a visible endpoint.

### Scope: changed tables plus one hop

Include every table the change creates, alters, or drops. Include each table that a shown edge also touches, as a context table. Drop every other table. Every edge then attaches to a visible box. The diagram stays small.

### Table change state

Add an optional `change` value to a `TABLES` entry.

| `change` | Meaning | Style |
| --- | --- | --- |
| `"new"` | The change creates this table. | Green border and a `new` tag. |
| `"changed"` | The change alters fields on this table. | Amber border and a `changed` tag. |
| `"removed"` | The change drops this table. | Red border, a `removed` tag, and a struck-through title. |
| (omitted) | A context table. | Normal border, dimmed. |

Mark a context table with `context: true`. The render dims it. The reader then sees the changed tables first.

### Field change state

Add an optional `change` value to a field. A changed table then shows which fields move.

| Field `change` | Meaning | Marker |
| --- | --- | --- |
| `"added"` | The change adds this field. | A green `+` before the name. |
| `"changed"` | The change alters this field's type, nullable state, or constraint. | An amber `~` before the name. |
| `"removed"` | The change drops this field. | A red `−` before the name, struck through. |
| (omitted) | An unchanged field. | No marker. |

Keep a removed field in place and strike it through. The reader needs the old state and the new state in one view.

### Legend and palette

Show every present change state in the legend. Show these legend entries in change mode only. Reuse the palette: `--ok` for new and added, `--amber` for changed, and a red variable for removed. Add the red variable when the file lacks one.

### The audit still runs

Change mode relaxes no layout rule. Run `auditLayout()`. A context table counts as a table for the overlap and gap checks.

## The built-in layout audit (required)

Every diagram ships a small `auditLayout()` that runs once at load and `console.warn`s on:

- any two table boxes that overlap, or sit closer than 24 px;
- any table that extends outside its group's derived region (only possible in legacy hand-sized docs);
- any `note` longer than 30 words.

```js
function auditLayout(rects) {           // rects: [{id, x, y, w, h}]
  for (let i = 0; i < rects.length; i++) {
    for (let j = i + 1; j < rects.length; j++) {
      const a = rects[i], b = rects[j], gap = 24;
      const clear = a.x + a.w + gap <= b.x || b.x + b.w + gap <= a.x ||
                    a.y + a.h + gap <= b.y || b.y + b.h + gap <= a.y;
      if (!clear) console.warn(`layout: ${a.id} and ${b.id} overlap or sit closer than ${gap}px`);
    }
  }
  for (const t of TABLES) {
    const words = (t.note || "").trim().split(/\s+/).filter(Boolean).length;
    if (words > 30) console.warn(`note: ${t.id} has ${words} words (cap is 30)`);
  }
}
```

After any edit, open the file and check the console. A clean console is part of "done".

## Rendering architecture

- **Tables are positioned HTML** (`div` per table, absolute `left/top` from `x/y`), built with `createElement`/`textContent` — never `innerHTML`.
- **Edges are one SVG layer** behind or above the tables, sized to the derived canvas. Each edge routes from box edge to box edge; the edge `kind` picks the dash pattern; a mid-edge label is optional and short.
- **Click a table to focus it**: its edges and neighbors highlight; everything else dims. Click empty canvas to clear.
- **Legend** for badges and edge kinds. **Header** with the schema name and source commit or date.
- **Pan and zoom** (drag + buttons) when the schema is larger than one screen; a `fit` control frames the whole canvas.
- Palette as `:root` CSS variables; system font stacks; the whole page works offline.
- **Pan and zoom the canvas**: drag to pan, plus zoom in / zoom out / fit controls. Distinguish a drag from a click with a small movement threshold, so click-to-focus still works.

## Footguns

- **A scriptless viewer shows an empty page.** The diagram renders with JavaScript into an empty canvas element. Any real browser and any static host (GitHub Pages, `file://`) work. Embedded preview panels that render snapshots without scripts show nothing. Ship a `<noscript>` notice, and when someone reports "the document is empty," check the viewer in a real browser before you debug the code.

## Language rules

Every human-readable string — group labels, captions, tags, notes, edge labels, legend text — MUST follow the [`asd-ste100`](../asd-ste100/SKILL.md) skill, strictly. Table and field names are identifiers: render them exactly as the source spells them.

## Verify before finishing

- The console shows zero `auditLayout` warnings.
- Every table from the source appears once; no invented tables or fields; spot-check five fields against the source.
- Every relationship in the source appears as an edge; every edge kind is in the legend.
- Click-to-focus works on the first and the last table; clearing works.
- Zero external requests. No `innerHTML`.
- Every note is 30 words or fewer.
- In change mode: the legend shows every change state present, and every shown edge attaches to a visible table.

## Reference example

[`examples/bookstore-schema.html`](examples/bookstore-schema.html) is a complete working diagram: seven tables in three derived-region groups, computed heights, the edge legend, click-to-focus, and the layout audit. Copy it as a skeleton and replace the three data arrays.
