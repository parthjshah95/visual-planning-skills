# Visual Planning Skills

Three small, tool-agnostic [agent skills](https://docs.claude.com/en/docs/claude-code/skills) for
turning ideas into things you can *look at* before you build them:

| Skill | What it makes | Trigger |
| --- | --- | --- |
| **`visual-explainer`** | A single, self-contained interactive HTML explainer — hand-drawn inline-SVG illustrations, an animated scene player or pipeline, mermaid-style diagrams, a glossary. No CDNs, no build step, opens offline. | "illustrate / explain / visualize how X works as a web page" |
| **`visual-plan`** | A visual, interactive HTML plan for a change: a diagram-led explanation grounded in the real code, plus every decision as a multiple-choice card you answer in the browser. You review, override in chat, and the agent records the approved plan wherever you track work. | "plan this change so I can review it before you build it" |
| **`challenge-plan`** | An adversarial simplification review of an AI-authored plan, run by a *different* model. It can only cut, reuse, simplify, align to convention, or ask the human — never add scope. Returns `SATISFIED` or `REVISE`. | run it on a drafted plan when you want a second model to attack it for over-engineering |

They compose but don't require each other:

- `visual-plan` **builds on** `visual-explainer`'s drawing patterns.
- `challenge-plan` is a **separate, on-demand** pass. `visual-plan` does not run it for you — you decide when a plan is worth challenging, so you never pay for a review round you didn't want.

Written as plain `SKILL.md` files, so any agent that can read a skill can use them — Claude Code is the reference harness.

## Install

### As a Claude Code plugin (recommended)

```bash
claude plugin marketplace add parthjshah95/visual-planning-skills
claude plugin install visual-planning-skills@visual-planning-skills
```

Then invoke a skill by name in a session: `/visual-explainer`, `/visual-plan`, `/challenge-plan` — or just describe the task and let the agent pick.

### By hand (any agent)

Copy the skill directories into wherever your agent loads skills from. For Claude Code that's `~/.claude/skills/`:

```bash
git clone https://github.com/parthjshah95/visual-planning-skills
cp -R visual-planning-skills/skills/* ~/.claude/skills/
```

Each `skills/<name>/SKILL.md` is self-contained. The `visual-explainer` skill also ships a reference example at `skills/visual-explainer/examples/pipeline-explainer.html` — open it in a browser to see every pattern working.

## Plan profiles — keep your process out of the skill

A plan is only "done" relative to a workflow. One team merges straight to trunk; another has a dev environment, a prod monitoring window, and a sign-off. Hardcoding either into the skill makes it useless to the other team, so `visual-plan` keeps that contract in an **optional plan profile** instead.

- Pass one with `profile=<path>`, or drop a `.plan-profile.md` at your workspace root.
- With no profile, the skill uses a generic default: goal, the change shown visually, an implementation outline, "how we'll know it worked," and whatever decisions the change actually raises.
- A profile adds three things only: extra **required sections**, extra **required decisions** (rendered as decision cards), and where the approved plan is **recorded**.

### Example profile — a dev → prod pipeline

Save as `.plan-profile.md`. This turns the generic default into a plan with a dev test plan, a prod monitoring plan, and four fixed decisions — the kind of contract a team with staged environments needs. Adapt or delete freely.

```markdown
# Plan profile — staged dev/prod delivery

## Required sections
- **Dev integration test plan** — environment, concrete steps, observable expected results,
  smoke tests, and the logs/metrics to check after merge to the dev branch.
- **Prod testing and monitoring plan** — at least one production-only validation step, a concrete
  monitoring window (not "until it looks fine"), objective failure criteria (a number or a log
  signature), a rollback-or-fix-forward choice with steps, and who gets notified.

## Required decisions
- Pause for human PR review before merging to the dev branch? (default: no, for low-risk changes)
- Dev testing strategy — confirm the concrete steps and expected results.
- Prod testing strategy — confirm the production validation steps and rollback choice.
- Extended monitoring required? If yes, duration and thresholds; if no, why standard monitoring is enough.

## Record the approved plan in
- The project's tracker ticket description. Move the ticket to the "ready to start" state on approval.
```

## Why these exist

- **`visual-explainer`** — most "explain this system" output is prettified docs. An explainer that *animates the real mechanism*, walks one concrete example end-to-end, and defines its terms teaches far better — and a single offline HTML file travels anywhere.
- **`visual-plan`** — a plan you read as prose is a plan you skim. A plan you *see* — the failure animated, the data flow moving, each decision as a card with a recommended default — gets reviewed properly, and the review is a few clicks plus one chat message.
- **`challenge-plan`** — the specific way AI plans fail is over-building: an under-specified requirement gets the defensive reading, and machinery grows for needs nobody has. A different model, told it may only *subtract*, is a cheap and effective counterweight.

## License

MIT — see [LICENSE](LICENSE).
