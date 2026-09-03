# Visual Planning Skills

Struggling to understand the giant walls of text your AI throws at you? Frustrated by jargon AI invents that only it can fathom?

## You are not alone.

No one understands AI these days.

![Six slides: real posts about AI jargon walls](assets/deck.gif)

**[Open the interactive explainer →](https://parthjshah95.github.io/visual-planning-skills/skills/visual-plan/examples/visual-plan-explainer.html)** It plays this deck with controls. It shows the whole flow, a live decision card, and install steps for eight agents.

<sub>Slide credits: Steve Yegge (the workflow comic); the r/ClaudeAI community: the moderator-bot summary, u/nightbunnies, u/endlesskitty, u/Careless_Leg_4905; the Swole Doge format. The ASD-STE100 subskill draws on [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill).</sub>

## The fix

![A wall of gray text turns into a small drawn plan with one decision card](assets/hero.svg)

`visual-plan` draws the plan. `asd-ste100` keeps the words plain. Decision cards ask questions you can answer.

## The skills

| Skill | What it does |
| --- | --- |
| **`visual-explainer`** | "Visually explain how the code works." Creates an HTML file with animations and diagrams. |
| **`visual-plan`** | "Visually plan this task." Replaces the plan mode with an HTML version of it. Less text, more interactivity. |
| **`visual-schema`** | "Visualize my database schema." Visually see the models, relationships, and fields on a draggable canvas. |
| **`challenge-plan`** | "Challenge this plan for over-engineering." A different model reviews the plan. It may only cut, never add. |

The skills work together, but none needs the others.

- `visual-plan` reuses the drawing patterns from `visual-explainer`.
- `challenge-plan` is separate. `visual-plan` never runs it for you. You run it when a plan needs a check.

## `visual-explainer` example

![The animated explainer that visual-explainer produces](assets/explainer-demo.gif)

### [▶&nbsp;&nbsp;View it live on GitHub Pages](https://parthjshah95.github.io/visual-planning-skills/skills/visual-explainer/examples/pipeline-explainer.html)

<sub>Above: `visual-explainer` explains one subject, how a deploy pipeline works. A scene player walks the mechanism step by step. Source: [`pipeline-explainer.html`](skills/visual-explainer/examples/pipeline-explainer.html).</sub>

## `visual-plan` example

![The animated visual plan that visual-plan produces](assets/plan-visual.gif)

### [▶&nbsp;&nbsp;View it live on GitHub Pages](https://parthjshah95.github.io/visual-planning-skills/skills/visual-plan/examples/csv-export/plan.html)

<sub>Above: `visual-plan` plans one small feature, *Add CSV export to the Reports page*. It shows the change as an animation. It turns the one real decision into a card you answer in the browser. Source: [`plan.html`](skills/visual-plan/examples/csv-export/plan.html).</sub>

## `visual-schema` example

![The interactive schema diagram that visual-schema produces](assets/schema-demo.gif)

### [▶&nbsp;&nbsp;View it live on GitHub Pages](https://parthjshah95.github.io/visual-planning-skills/skills/visual-schema/examples/bookstore-schema.html)

<sub>Above: `visual-schema` draws a small bookstore database. The tables come from the model source. Click a table to see its relationships. Drag to pan, zoom to fit. Source: [`bookstore-schema.html`](skills/visual-schema/examples/bookstore-schema.html).</sub>

## Examples

Every example is one self-contained HTML file. Open the live link, or download the source and open it in a browser.

| Example | Made with | Open |
| --- | --- | --- |
| Deploy-pipeline explainer | `visual-explainer` | [live](https://parthjshah95.github.io/visual-planning-skills/skills/visual-explainer/examples/pipeline-explainer.html) · [source](skills/visual-explainer/examples/pipeline-explainer.html) |
| The visual-plan explainer (the deck above) | `visual-explainer` | [live](https://parthjshah95.github.io/visual-planning-skills/skills/visual-plan/examples/visual-plan-explainer.html) · [source](skills/visual-plan/examples/visual-plan-explainer.html) |
| CSV-export plan | `visual-plan` | [live](https://parthjshah95.github.io/visual-planning-skills/skills/visual-plan/examples/csv-export/plan.html) · [source](skills/visual-plan/examples/csv-export/plan.html) |
| Bookstore schema | `visual-schema` | [live](https://parthjshah95.github.io/visual-planning-skills/skills/visual-schema/examples/bookstore-schema.html) · [source](skills/visual-schema/examples/bookstore-schema.html) |

## Install

Clone the repo once. Then copy the skill folders to where your agent loads skills.

```bash
git clone https://github.com/parthjshah95/visual-planning-skills
cd visual-planning-skills
```

| Agent | Copy the skills to |
| --- | --- |
| Claude Code | `cp -R skills/* ~/.claude/skills/` |
| Codex / ChatGPT | `cp -R skills/* ~/.codex/skills/` |
| Cursor | `cp -R skills/* ~/.cursor/skills/` |
| OpenCode | `cp -R skills/* ~/.config/opencode/skills/` |
| OpenClaw | `cp -R skills/* ~/.openclaw/skills/` |
| Hermes | `cp -R skills/* ~/.hermes/profiles/<profile>/skills/` |
| Windsurf (per project) | `cp -R skills/* <project>/.windsurf/skills/` |
| Antigravity (per workspace) | `cp -R skills/* <workspace>/.agents/skills/` |

Each `SKILL.md` is self-contained.

## Custom instructions

<details>
<summary>Optional: tell the skills about your team's process.</summary>

<br>

A finished plan means different things to different teams. One team merges straight to trunk. Another team needs a dev environment, a monitoring window, a sign-off, a house style, a place to publish, and a tracker. So the skills keep all of that in one optional file, not in the skills.

- Pass a file with `instructions=<path>`, or drop a `custom-instructions.md` file at your workspace root.
- With no file, the skills use their defaults: a goal, a picture of the change, the steps, a check that it worked, and the open decisions.
- The file has seven optional headings. `visual-plan` reads all of them. `visual-explainer` reads `## Style` and `## Output`. A heading you leave out keeps its default.

| Heading | Sets |
| --- | --- |
| `## Style` | Writing-rule files to read before any text is written. |
| `## Output` | Where the HTML goes, what to run to publish it, and what to report. |
| `## Required sections` | Extra sections a finished plan must contain. |
| `## Required decisions` | Extra decisions shown as cards. |
| `## Challenge` | Whether a different model attacks the plan automatically, how many rounds, and how it is invoked. |
| `## Record the approved plan in` | The tracker, the exact read and write commands, and the state to move the ticket to. |

The file holds settings only. It never restates a step of a skill, so a skill update reaches every team without edits to their files.

### Example: a staged delivery pipeline

Save this as `custom-instructions.md`. Change or delete any heading as you need.

```markdown
# Custom instructions: staged dev/prod delivery

## Style
- docs/writing-rules.md

## Output
- Path: docs/plans/<YYYY-MM-DD>_<slug>.html
- Publish: ./scripts/publish-internal.sh <file>
- Report: the URL that the publish step prints

## Required sections
- **Dev test plan**: the environment, the steps, the expected results, and the logs to check.
- **Prod monitoring plan**: one production-only check, a fixed monitoring window, the failure
  threshold, the rollback choice, and who to notify.

## Required decisions
- Pause for a human PR review before the dev merge? (default: no, for low-risk changes)
- Confirm the dev test steps and expected results.
- Confirm the prod validation steps and the rollback choice.
- Is extended monitoring needed? If yes, give the window and thresholds.

## Challenge
- Run: yes
- Rounds: 3
- Challenger: docs/challenger-commands.md
- Stalemate: a decision card with the simpler option pre-selected

## Record the approved plan in
- The tracker ticket. Read it with `tracker show <id>`; write the plan with `tracker update <id> --body-file <plan.md>`.
- Move the ticket to "ready to start" on approval.
- Conventions: docs/ticket-conventions.md
```

</details>

## License

MIT. See [LICENSE](LICENSE).
