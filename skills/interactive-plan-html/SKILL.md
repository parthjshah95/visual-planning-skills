---
name: interactive-plan-html
description: Generate a visual, interactive HTML plan for a task in one pass. No sequential question loop — the AI reads context, builds a diagram-led plan with encouraged but optional animations, and presents decisions as multiple-choice cards with pre-selected defaults. The user reviews it in a browser, overrides decisions in chat, and the agent writes the approved plan wherever the project tracks work. Use when the user wants a reviewable plan for a change before any code is written.
---

# Interactive Plan HTML

Generate a visual, interactive HTML plan in one pass. The user reviews it in a browser, overrides decisions in chat, and the agent records the approved plan wherever the project keeps its plans. No sequential question loop.

## Invocation

```text
/interactive-plan-html <task description or ticket reference> [workspace=<path>] [profile=<path>] [out=<dir>] [notes]
```

Examples:

- `/interactive-plan-html "Pre-warm the connection pool at deploy time"` — plan a free-form task.
- `/interactive-plan-html PROJ-1234` — plan against an existing tracker ticket, if the project uses one.
- `/interactive-plan-html "Add CSV export to the reports page" profile=./.plan-profile.md out=./plans`

If the workspace is ambiguous, ask which repo or worktree before any tool call.

## Core Contract

- **AI owns the plan.** Do not ask the user what they want to discuss. Build the full plan yourself from the task, the repo, and any supplied context. Present it; let the user correct it.
- **One-pass generation.** No question loop. Generate the entire plan — visual explanation, implementation steps, verification, and decisions — in a single pass, then present it as one interactive HTML file.
- **Decisions as multiple-choice cards, not a question loop.** Every decision the user needs to make is a radio-button card with the AI's recommendation pre-selected. The user only intervenes on disagreements.
- **Ask, don't guess, on intent.** Where the task under-specifies *what the result should do*, do not silently fill the gap with the rich, defensive reading. Surface each material gap as an intent card asking the behavioral question, with the reading that needs the least machinery pre-selected. Only ask when different answers change what gets built; otherwise take the simple reading and record it as a one-line assumption the user can veto.
- **Plain language is mandatory.** Every question, option, diagram label, and explanation follows the plain-language rules below.
- **Animation encouraged, never compulsory.** Start by considering an animated scenario, scene player, or moving data flow, because progressive storytelling often makes a change easier to understand. Use animation when it adds explanatory value; never force motion that is decorative, fragile, or contrary to the user's request.
- **Intelligent pruning.** Skip decisions the codebase, the task, or repo docs already answer. For low-risk work, infer safe defaults, pre-select them, and only surface decisions that materially change scope, risk, verification, or rollout.
- **Completeness is defined by a plan profile, not baked in.** What sections and decisions a finished plan *must* contain depends on the team's downstream workflow. That contract lives in an optional **plan profile** (see below), never hardcoded into this skill. With no profile, use the generic default profile.
- **Record only after approval.** Once approved, write the compact plan where the project tracks work (see *Recording the plan*) and exit.
- **No code, no branches, no deploys.** This skill plans. It never edits the repo (except the plan artifacts), opens PRs, or runs anything downstream.

## When NOT To Use This Skill

- Trivial changes (single-file fixes, doc-only edits, dependency bumps, typo fixes) — they do not need a plan.
- The user wants you to think out loud about a design without producing a recorded plan — answer in chat; do not invoke this skill.

## Plan Profiles — how completeness is defined

A **plan profile** is a short markdown file that lists the extra sections and decisions a plan must contain to be "done" for a given team or workflow. This is the seam that keeps team- or pipeline-specific requirements *out* of the skill.

- If the user passes `profile=<path>`, or a file named `.plan-profile.md` exists at the workspace root, read it and treat its required sections and decisions as mandatory. Every one becomes content in the plan and, where it is a choice, a decision card.
- If no profile is found, use the **generic default profile** below.

The profile controls three things only: **(1)** extra required sections (e.g. a test plan, a rollout plan, a security review), **(2)** extra required decisions (rendered as decision cards), and **(3)** where the approved plan is recorded (see *Recording the plan*). It does not change how the visual explanation or decision cards are built.

### Generic default profile (used when no profile is supplied)

A finished plan must contain:

1. **Goal** — one or two sentences: what changes and why, plus explicit non-goals.
2. **The change, shown visually** — the visual explanation section (the centerpiece).
3. **Implementation outline** — the ordered steps, with file/module names.
4. **How we'll know it worked** — the concrete way to verify the change does what the goal says: the check to run, the observable result, and what "failed" looks like. Depth scales with risk; a one-line manual check is a valid answer for a small change.
5. **Decisions** — every choice the change actually raises, as decision cards. There is no fixed list; surface what this change needs (a data-shape change, a flag, an ordering, a rollout choice) and prune what it doesn't.

> A team with a heavier process (staged environments, mandatory monitoring windows, sign-offs) encodes that as a profile file instead of asking this skill to assume it. An example profile lives in the repo README.

## Inputs

- A task description **or** a tracker ticket reference.
- Optional: workspace path. If omitted and the current directory is unambiguous, use it; otherwise ask.
- Optional: a plan profile path.
- Optional: an output directory for the artifact (default `./plans/`).
- Optional: notes from the user (focus areas, constraints, deadlines).

## Walkthrough

### 1. Resolve the planning target

**Ticket reference supplied:** open it with whatever the project uses (a CLI, an API, the tracker UI via the user). Read its title, description, comments, and links. Before any write to the ticket, save a scratch snapshot of the original text (session scratchpad or a gitignored dir; never commit it) so same-session edits stay attributable and you never rename current text "original."

**Free-form task supplied:** capture the description as a working title; refine it during generation. If the project records plans in a tracker, create the ticket only *after* approval (step 6), not now.

### 2. Gather context

Read what you need to plan, no more:

- The task/ticket, plus any linked threads, PRs, dashboards, incidents, attachments.
- Repo entry points: `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/`, files named in the task.
- Cross-repo context when the task spans packages or services.
- **Read the actual code the plan will change.** Grep for symbols, open the handler files, read the data models. The visual explanation must be grounded in real code, not inferred from the task text.

Read-only probes only. **No edits except the plan artifacts.**

**Pin the baseline before making code claims.** Record the branch and exact commit the plan targets, the workspace path, and whether it is clean. If the workspace differs from the target, read the target with ref-aware commands (`git show <sha>:<path>`, `git grep <sha>`) rather than trusting a stale checkout.

### 3. Generate the HTML plan

Generate the full plan as a single self-contained HTML file. This replaces the question loop — behavior, architecture, verification, and decisions are all resolved in one pass and rendered visually.

**Resolve, in one pass:**

- **What the result does from the outside** — who is affected, the happy path step by step, what state the user/caller observes, the failure modes they see, and the goals and explicit non-goals.
- **How it is built** — affected repos/modules, data ownership and typed boundaries, any new or changed contracts (API, schema, event, config), cross-repo ordering, and the ordered implementation steps.
- **How it is verified** — whatever the active profile requires. For the generic default, that is the "How we'll know it worked" section.

**Keep architecture honest (lightweight provenance).** Every built thing should trace to something the result must do; every behavior should trace to the task text, a verified code fact, or a stated assumption. A built thing with no behavior behind it is invented — cut it or turn it into an intent card. A behavior with no source is an intent gap — surface it as an intent card. You do not need heavy audit tables for this; you need the discipline. (If you later run the optional `challenge-plan` skill, it asks for a fuller inventory — build that then, not now.)

**Draft the compact plan now, not at the end.** As you generate, write the short markdown plan you will record on approval (step 6). Carry two extra sections in it:
- `Assumptions` — each intent gap you filled with the simple reading, one line each.
- `Deliberately not built` — each thing you chose not to build now: what it is, where the seam is (the place a future change plugs in without rework), and what signal would make you build it.

**Intelligent pruning.** For each decision, try to draft a confident answer from repo/task/docs. If you can, pre-select it as the recommended option. Leave a decision open only when there is no defensible default.

#### HTML structure

One self-contained file (no CDN, no external deps), built with the patterns from the `illustrate-html` skill. Sections in order:

**1. Header.** Task/ticket id, title, one-line goal, a risk pill, and the step count. Nothing else.

**2. Visual explanation — the centerpiece.** Reuse relevant `illustrate-html` patterns. Prefer an animated scenario, scene player, or moving pipeline when the plan has a meaningful sequence, state change, or request flow. Animation is encouraged but optional: omit it when motion adds nothing, would make the artifact fragile, or the user asked for a static presentation.

Selection rules:
- **Animated scenario / scene player** — ordered workflows, user journeys, branching outcomes, event pipelines, lifecycle/state transitions, before/after behavior.
- **Static architecture / data-model / comparison diagram** — when the subject is structural with no temporal progression, or to support an animated explanation.
- **Static flowchart** — primarily as a complete-path overview slide inside an animated deck, or when the user explicitly asks for one. Do not pick a standalone flowchart merely because it is easier to build than animation.

Whenever a flowchart appears, render the entire chart in normal document flow. The page may be as long as needed: the visual section, slide, and flowchart container use content-driven height (`height: auto`, `max-height: none`, `overflow: visible`) with no fixed, viewport-relative, or capped height. Let the document grow to contain every node and label; never shrink, scale, clip, scroll-within, or overlap the chart to keep it short. Prefer CSS grid/flex for text-heavy nodes and stack branches responsively on narrow viewports. Decorative connectors may use pseudo-elements or absolute positioning only when they cannot cover content or affect the container's measured height.

What to visualize, by change type:

| Change type | What to visualize |
| --- | --- |
| **Bug / perf fix** | What's broken, root cause, how the fix works. Prefer an animated failure-to-fix sequence; add a static before/after when useful. |
| **Enhancement** | Current system (architecture diagram), what changes (highlighted on the diagram), data flow before/after. |
| **Greenfield feature** | Product concept (user-flow diagram or UI wireframe), proposed architecture, data-model visualization. |
| **Refactor** | Current structure, target structure, migration path. Morph toggle between before/after. |
| **Integration** | System-boundary diagram plus an animated happy-path data flow; a static full-path flowchart may serve as an overview slide. |

**Less text, more visual.** If you can draw it, don't write it. Annotations on diagrams replace paragraphs. The behavior and architecture content lives primarily here, not in prose blocks.

**3. Implementation pipeline.** A compact visual of the ordered steps. For cross-repo work, show the dependency chain with an arrow between step cards. Each step card lists the module/repo name and bullet-point scope.

**4. Verification (compact, expandable).** Render the verification the active profile requires as compact `<details>` cards — a `<dl>` of the required fields, brief. For the generic default, that is one "How we'll know it worked" card. If the profile requires more (a dev plan, a prod plan, a security section), render one compact card each. Keep them 3–5 lines each; expand into full prose only when recording the plan (step 6).

**5. Multiple-choice decision cards.** Each decision card has:
- A question title.
- **A change-specific explanation paragraph (mandatory).** 3–5 sentences grounding the question in *this* change. Name the actual functions, files, endpoints, and tradeoffs — never describe the concept generically. Bad: "Feature flags let you disable a change instantly." Good: "The fix replaces per-row `to_dict()` calls with one bulk query inside `prepare_results()`. A flag would let us switch between the old and new path at runtime."
- **Plain-language wording (mandatory).** The question asks about the practical choice, not the implementation concept; each option says what happens if selected.
- 2–4 options with one-line descriptions; the recommended one pre-selected and badged.
- **A mandatory "Other" escape hatch — last in every card.** One more radio labeled "Other" whose free-text input is *contained inside the Other option itself* (not a separate field below). It reads as one choice: "none of these — here's what to do instead." Focusing or typing in the field auto-selects the Other radio; clicking anywhere on the Other card selects it too. "Copy decisions" must capture the typed text (emit `Other — <typed text>`, or `Other — (unspecified)` if chosen but blank). Selecting "Other" always counts as changed-from-default. Author it inline per card, or inject it into every `.opts` group with a small load-time helper (`createElement`/`textContent`, never `innerHTML`).

**Intent-gap cards come first.** Render every material intent gap as its own card, before the implementation decisions. Ask the behavioral question — "while the workflow is temporarily broken, should new requests queue and run on recovery, or be rejected?" — never the mechanism question ("should we add an admission gate?"). Pre-select the reading that needs the least machinery and draw the v1 for that reading. The human corrects upward cheaply; a silent rich-reading guess becomes machinery nobody reviewed.

**Required decisions** = whatever the active profile lists, plus any change-specific decisions you identify (flag, response-shape change, cross-repo ordering, rollout strategy). The generic default profile requires no fixed decision list — surface what the change raises.

**Selection-capture controls — required at BOTH the top and bottom of the decisions section.** Render an **"Accept all defaults"** button and a **"Copy decisions"** button in two places: above the first card and after the last card. The plan is a static file with no server; a selection only leaves the browser when the user copies it. "Copy decisions" serializes the current radio state (flagging anything changed from its default) to the clipboard so the user can paste it back into chat — or they can just say "looks good" / "change Q3 to …". Wire both copies of the buttons to the same handlers (bind by class, not `id`) and flash a confirmation on every `.copy-note`. Add an inline hint by the bottom controls reminding the user they can paste the summary back or reply in chat.

**The "Copy decisions" handler must not depend on the async Clipboard API alone.** `navigator.clipboard.writeText` is blocked in a non-secure or sandboxed context — exactly the case when the plan is viewed inside a preview-panel iframe. Relying on it alone makes the button silently fail. Implement a fallback chain: (1) try `navigator.clipboard.writeText`; (2) on rejection or absence, use a temporary off-screen `<textarea>` + `document.execCommand("copy")`; (3) as a last resort, reveal a pre-selected `<textarea>` with the serialized decisions and flash "Select + ⌘/Ctrl+C to copy". Build every element with `createElement`/`textContent`, never `innerHTML`. The button must never dead-end on "Copy failed".

#### Technical rules

- Reuse the `illustrate-html` animation and scene-player patterns when they strengthen the explanation, not as mandatory boilerplate. Keep the output self-contained, avoid `innerHTML`, use system font stacks, and make diagrams responsive.
- If the visual uses a flowchart, verify `height: auto`, `max-height: none`, `overflow: visible` on the section/container. No internal scroll area, fixed aspect ratio, viewport-height cap, clipped SVG, or transform scaling to constrain its vertical size.
- Use a clean, professional palette — an engineering plan should feel like a well-designed dashboard, not an art-deco explainer.
- File goes to `<out>/<YYYY-MM-DD>_<slug>.html` (default `out` is `./plans/`). `<YYYY-MM-DD>` is today's date; `<slug>` is a short lowercase-hyphenated descriptor.

### 4. Stop condition (before showing the plan)

Verify **all** of these before opening the HTML:

- Every section and decision the active profile requires is present and passes its rules.
- The header states a clear goal.
- The visual explanation is grounded in actual code (real function names and file paths, not generic descriptions).
- Any animation present adds explanatory value; any standalone static flowchart was explicitly requested or is a supporting overview slide.
- If a flowchart is used, every node is visible without overlap or clipping, the section has no height cap or internal scrollbar, and the document expands to the chart's full height at desktop and narrow widths.
- The "Copy decisions" + "Accept all defaults" controls appear at both the top and bottom, both work (bound by class), and "Copy decisions" has the non-Clipboard-API fallback chain.
- Every decision card ends with an "Other" option whose free-text field is captured by "Copy decisions".
- The implementation pipeline covers every step with module names and scope.

Fix the HTML before presenting it. Do not show an incomplete plan.

### 5. Present the plan

1. Open the file: `open <out>/<YYYY-MM-DD>_<slug>.html` (macOS) / `xdg-open` (Linux) / `start` (Windows). Print the absolute path in chat.
2. Tell the user, in 2–3 sentences: the path, and that they can review it in the browser, then say "looks good" or override specific decisions ("change Q2 to Yes").

Do not paste the plan content into chat. The HTML is the presentation.

**Preview-panel workaround (when an embedded preview panel is blank / "Awaiting server…").** `open` launches the real browser and always works. A harness preview panel serves over `localhost` and breaks two ways: (a) the file lives in a path the panel can't serve — stage a copy inside the workspace (e.g. a gitignored `./.plan-preview/index.html`) and serve that; (b) a server bound IPv4-only (`python3 -m http.server --bind 127.0.0.1`) leaves the panel stuck, because it resolves `localhost` to IPv6 `::1` first. Serve dual-stack: bind `::` with `IPV6_V6ONLY=0` (a ~15-line `socketserver.TCPServer` subclass). Keep any such preview server and staged copy in a gitignored dir, out of tracked code.

### 6. Get approval, then record the plan

The user reviews the HTML and responds in chat:

- **"Looks good" / "approve" / "accept all defaults"** → record the plan.
- **"Change Q2 to B" / specific overrides** → record the overrides, then record the plan.
- **"Revise <section>"** → update the HTML for that section, re-open, show again.
- **"Reject"** → confirm whether to discard or shelve under a different filename.

#### Recording the plan

Where the approved plan goes is set by the active profile (or the user); this skill does not assume any one tracker. Pick the destination the project actually uses:

- **A tracker ticket (Linear, Jira, GitHub Issues, etc.)** — put the compact plan in the ticket description/body via whatever the project uses to write tickets (a CLI, an API, or by handing the text to the user to paste). Move the ticket to the project's "ready to start" state if it has one. For a free-form task with no ticket yet, create the ticket now, after approval.
- **A file in the repo** — write the compact plan to a markdown file next to the HTML (e.g. `<out>/<YYYY-MM-DD>_<slug>.md`) and reference the HTML from it.
- **Nothing** — if the user only wanted the artifact, the HTML is the deliverable; stop after presenting it.

The **compact plan** (markdown) contains:
- Summary: goal, risk level, step count — a few lines.
- Every section the active profile requires, expanded from the compact HTML cards into full prose.
- The implementation outline (ordered steps with module names).
- Decision values (every answer, noting which changed from the default).
- `Assumptions` — the simple-reading gap fills the user's approval confirmed.
- `Deliberately not built` — one line per entry: the deferred thing → the seam that keeps it pluggable → the signal that would activate it.
- `Visual plan:` — the path to the HTML file.

Give the tracker **structure**, not a thesis. The HTML file is the human-readable reference.

### 7. Exit

Tell the user:
- Where the plan was recorded (ticket URL, or file path), if anywhere.
- The absolute path to the HTML file.
- Optionally, that they can run `/challenge-plan` next to have a different model attack the plan for over-engineering before execution (see below).

## Optional: adversarial simplification review

After the plan is presented or approved, the user may run the separate [`challenge-plan`](../challenge-plan/SKILL.md) skill: a *different* model attacks the plan for invented requirements, invented trust boundaries, and speculative structure, and either confirms it or proposes cuts. This skill does **not** run it for you — it is a deliberate, user-triggered step, so you never pay for a challenge round the user didn't want. Offer it; don't force it.

## Plain-language rules (apply to every human-readable string in the plan)

- **Behavior before mechanism.** Say what the change does and what the user observes before naming internal machinery.
- **Define every non-obvious term before first use.** No undefined shorthand carried forward.
- **Prefer the plain word;** spell out abbreviations once.
- **Short, active sentences;** one idea each.
- **One term per concept;** don't rotate synonyms.

Never apply these to code, identifiers, quoted material, or exact strings.

## Completion checklist

- [ ] Planning target resolved (ticket opened, or free-form task captured for later).
- [ ] Baseline pinned: target branch and commit recorded; code claims checked against it, not a stale checkout.
- [ ] HTML plan written to `<out>/<YYYY-MM-DD>_<slug>.html`. Date is today; slug is lowercase-hyphenated.
- [ ] Visual explanation grounded in actual code — real functions, files, endpoints.
- [ ] Animation treated as encouraged, not compulsory; any motion improves comprehension.
- [ ] Any flowchart is fully visible in normal flow with unbounded content-driven height, no overlap/clipping, no internal scroll.
- [ ] Every section and decision the active profile requires is present (generic default if no profile).
- [ ] Material intent gaps surfaced as behavioral intent cards with the simplest reading pre-selected.
- [ ] Compact plan drafted at generation time with `Assumptions` and `Deliberately not built`.
- [ ] "Copy decisions" + "Accept all defaults" at both top and bottom, wired by class; "Copy decisions" has the Clipboard-API → `execCommand` → manual-`<textarea>` fallback chain.
- [ ] Every decision card ends with an "Other" option whose free-text field is captured by "Copy decisions".
- [ ] Every decision-card explanation is change-specific, not generic.
- [ ] Every question, option, label, and explanation follows the plain-language rules.
- [ ] User approved (or overrode specific decisions).
- [ ] Approved plan recorded where the project tracks work (or intentionally left as the HTML only).
- [ ] No code changes, branches, PRs, or deploys triggered.

## Anti-patterns

- **Generic decision-card explanations.** "Feature flags let you disable a change instantly" describes the concept, not this change. Name the actual functions, files, tradeoffs.
- **Jargon-first questions.** "Which delivery semantics should the scheduler guarantee?" makes the reader decode the implementation. Ask "If it crashes mid-send, should it try again?"
- **Coining labels instead of explaining.** Inventing a compact term for a one-off idea and making cards carry it.
- **Wall-of-text verification cards.** 3–5 lines each in compact form; expand only when recording.
- **Prose where a diagram works.** Three paragraphs explaining an architecture should have been a drawing.
- **Missing visual explanation.** The visual section is the centerpiece, not optional. Every plan has at least one diagram.
- **Compulsory animation.** Encourage it; don't add motion that contributes nothing or fights an explicit request.
- **Standalone static flowchart as the default.** Use it as an overview slide within an animated deck, or when the user explicitly asks — not because it is easier than animation.
- **Constrained flowchart canvas.** No fixed-height, viewport-height, aspect-ratio, clipped, scaled, or internally scrolling container. The document grows to show the whole chart.
- **Skipping the code read.** If the visual doesn't name real functions and file paths, you skipped step 2.
- **Baking team process into the skill.** Mandatory environments, monitoring windows, and sign-offs belong in a plan profile, not in this skill.
- **A "Copy decisions" button that only calls `navigator.clipboard.writeText`.** It fails silently in a sandboxed iframe. Always include the `execCommand` → manual-`<textarea>` fallback.
- **Serving the preview IPv4-only.** Leaves the panel stuck on "Awaiting server…". Serve dual-stack.
- **Silently filling an intent gap with the rich reading.** Under-specified intent is a question for the human, not a license to build defensively.
- **Recording the plan before the user approves it.**
- **Pasting the HTML content into chat at approval time** — the HTML is the presentation.

## What this skill does NOT do

- No sequential question loop — the visual plan and decision cards replace the back-and-forth.
- No automatic challenge round — `challenge-plan` is a separate, user-triggered skill.
- No code changes, branches, PRs, or deploys.
- No assumption about which tracker (if any) the team uses — that is set by the profile or the user.
