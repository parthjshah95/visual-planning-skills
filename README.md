# Visual Planning Skills

Three small [agent skills](https://docs.claude.com/en/docs/claude-code/skills). Each one makes a change into something you can look at before you build it. Any agent that reads a `SKILL.md` file can use them.

![The animated visual plan that visual-plan produces](assets/plan-visual.gif)

<sub>Above: `visual-plan` plans one small feature, *Add CSV export to the Reports page*. It shows the change as an animation. It turns the one real decision into a card you answer in the browser. Source: [`plan.html`](skills/visual-plan/examples/csv-export/plan.html) · [view it live](https://htmlpreview.github.io/?https://github.com/parthjshah95/visual-planning-skills/blob/main/skills/visual-plan/examples/csv-export/plan.html).</sub>

| Skill | What it makes | Trigger |
| --- | --- | --- |
| **`visual-explainer`** | One self-contained HTML file that shows how something works. It has inline-SVG art, an animated scene player, hand-built diagrams, and a glossary. No CDN. No build step. It opens offline. | "illustrate / explain / visualize how X works as a web page" |
| **`visual-plan`** | A visual HTML plan for a change. The diagram comes from the real code. Each decision is a card you answer in the browser. You review it and override in chat. The agent records the result. | "plan this change so I can review it first" |
| **`challenge-plan`** | A different model reviews an AI-authored plan. It may only cut, reuse, simplify, or ask — never add scope. It returns `SATISFIED` or `REVISE`. | "check this plan for over-engineering" |

The skills work together, but none needs the others.

- `visual-plan` reuses the drawing patterns from `visual-explainer`.
- `challenge-plan` is separate. `visual-plan` never runs it for you. You run it when a plan needs a check.

## Install

### As a Claude Code plugin (recommended)

```bash
claude plugin marketplace add parthjshah95/visual-planning-skills
claude plugin install visual-planning-skills@visual-planning-skills
```

Then call a skill by name: `/visual-explainer`, `/visual-plan`, or `/challenge-plan`. Or describe the task and let the agent choose.

### By hand (any agent)

Copy the skill folders to where your agent loads skills. For Claude Code, that is `~/.claude/skills/`:

```bash
git clone https://github.com/parthjshah95/visual-planning-skills
cp -R visual-planning-skills/skills/* ~/.claude/skills/
```

Each `SKILL.md` is self-contained. `visual-explainer` ships an example, [`pipeline-explainer.html`](skills/visual-explainer/examples/pipeline-explainer.html). Open it in a browser.

## Custom instructions

<details>
<summary>Optional — set what a finished plan must contain for your team.</summary>

<br>

A finished plan means different things to different teams. One team merges straight to trunk. Another team needs a dev environment, a monitoring window, and a sign-off. So `visual-plan` keeps that contract in an optional file, not in the skill.

- Pass a file with `instructions=<path>`, or drop a `custom-instructions.md` file at your workspace root.
- With no file, the skill uses a default: a goal, a picture of the change, the steps, a check that it worked, and the open decisions.
- A `custom-instructions.md` file adds three things only: extra required sections, extra required decisions (each one becomes a card), and where the agent records the approved plan.

### Example — a staged delivery pipeline

Save this as `custom-instructions.md`. It adds a dev test plan, a prod monitoring plan, and four fixed decisions. Change it or delete it as you need.

```markdown
# Custom instructions — staged dev/prod delivery

## Required sections
- **Dev test plan** — the environment, the steps, the expected results, and the logs to check.
- **Prod monitoring plan** — one production-only check, a fixed monitoring window, the failure
  threshold, the rollback choice, and who to notify.

## Required decisions
- Pause for a human PR review before the dev merge? (default: no, for low-risk changes)
- Confirm the dev test steps and expected results.
- Confirm the prod validation steps and the rollback choice.
- Is extended monitoring needed? If yes, give the window and thresholds.

## Record the approved plan in
- The tracker ticket. Move the ticket to "ready to start" on approval.
```

</details>

## Why

- `visual-explainer` — an animation of the real mechanism teaches better than prettified docs.
- `visual-plan` — a plan you see gets reviewed. A plan you read gets skimmed.
- `challenge-plan` — AI plans fail because they over-build. A second model that may only cut is the counterweight.

## License

MIT — see [LICENSE](LICENSE).
