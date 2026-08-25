---
name: challenge-plan
description: Adversarial simplification review of an AI-authored plan, run by a different model before the plan is finalized. It may only push toward deletion, reuse, simplification, convention alignment, or a question for the human — a challenge that adds scope is invalid, even when labeled non-negotiable. Returns SATISFIED or REVISE. Run it on demand after a plan is drafted (for example, one produced by interactive-plan-html).
---

# Challenge Plan — Adversarial Review Of AI-Authored Plans

AI-authored plans fail one way more than any other: **under-specified intent → the authoring AI fills the gap with the rich, defensive reading (guessing too little feels negligent) → invented requirements or invented trust boundaries → architecture for requirements nobody has.** This skill breaks that chain: a *different* model attacks the plan's assumptions before it is finalized. The organizing principle, applied verbatim:

> **Simplicity preserves optionality; speculative structure is how future work gets manufactured.**

## When It Runs, Who Runs It

- **On demand.** Run it after a plan is drafted — for example, a plan produced by [`interactive-plan-html`](../interactive-plan-html/SKILL.md), which does *not* invoke this skill automatically. A calling skill or a human decides when to challenge, and owns any round cap and stalemate handling.
- **The challenger must be a different model/agent than the author.** Same-model, fresh-context is a last resort, not the goal — an author rarely finds the assumption it just made. Invoke a genuinely different model however your environment allows (a second CLI agent, an API call to another model family, a different local model). If no different challenger can be reached after a reasonable attempt, proceed with the plan but record `Simplification challenge: skipped — <reason>` in the plan and say so plainly. Never skip silently.

## The Mandate — One Direction Only

The challenger may **cut**, **replace with something that already exists**, **simplify**, **align with convention**, or **convert an element into a question for the human**. Nothing else. Converting an invented requirement into an intent question is not scope — it is the preferred remedy when the gap is real.

**A challenge that adds scope is invalid — even when labeled `non-negotiable`.** Additions are how adversarial review becomes a second engine of over-engineering. The only additions that qualify are this closed floor list:

- Tests for **genuinely new behavior** (not for unchanged behavior or a changed constant).
- Error handling that prevents **data loss**.
- Input validation, authentication, or authorization at a **real** trust boundary (defined below).
- Accessibility basics.
- Anything the human **explicitly requested**.

Nothing outside that list qualifies. In particular, these are **never** non-negotiables:

- **Hardening, precision, robustness:** wrappers, wall-clock deadlines, retries, guards, and enforcement machinery for a figure the human stated. Real pattern: a human set a 35-second timeout; the challenger demanded a wrapper "to enforce it" and tagged it non-negotiable. Invalid — a stated value is not a missing control.
- **Tests for unchanged behavior or config-value changes.** A constant is not new behavior.
- **Observability, metrics, alerts, performance work** — unless explicitly requested.

When an addition genuinely seems necessary, the finding may **ask the human** — it may never add.

**Trust boundaries are claimed, not assumed.** A trust boundary is where data crosses from systems you do not control into yours (a user's form input, a partner webhook, an uploaded file, words spoken on a call). Internal edges — your service calling your service, your code reading your own database — are **not** trust boundaries; re-validating there is defensive duplication (`misclassified-boundary`). To defend complexity as a security non-negotiable, the author must name **(a)** the untrusted party or concrete failure and **(b)** why no existing control — TLS, access control, encryption at rest, signature verification, a database constraint — already covers it. Covered threat ⇒ cut. Never re-implement a platform or contractual guarantee in application code.

## Inputs The Author Supplies

One challenge prompt (a scratch file, never committed) containing:

1. **Source ledger** — verbatim: direct human instructions; the pre-existing task/ticket text; any same-session agent-authored edits to that text (agent wording is a hypothesis, never authority — presenting it as human or pre-existing intent is a High `provenance-laundering` finding); relevant comments with author, timestamp, and any condition attached (a conditional comment is intent only while its condition holds).
2. **The compact plan** — behavior, architecture, implementation sequence — with the `Assumptions` and `Deliberately not built` sections.
3. **Baseline manifest per repo** — branch, target commit, workspace path, workspace-vs-target, clean/dirty. Every code claim is checked at the target commit (`git show <sha>:<path>`, ref-aware grep). A missing, stale, or unreadable baseline is a High `stale-baseline` finding before any design judgment.
4. **Planned-construct inventory** — every table, endpoint, config, secret, job, helper, dependency, metric, and alert labeled `reuse` | `change` | `new` | `unresolved`, with evidence. `unresolved` resolves to omission or a human question — never invented scope.
5. **Evidence register** — checks for anything code alone cannot prove, and each data claim labeled `existence` | `bound` | `prevalence`. A sample proving a thing exists cannot support a claim about how often it happens (`insufficient-evidence`).
6. **Repos in scope.**
7. **User-mandated elements** — exempt; never relitigated.
8. **On re-rounds** — what changed since the last verdict, plus author rebuttals with evidence.

## Scope

**Audited:** design substance — the behavioral spec, every proposed table/endpoint/config/gate/abstraction/migration, the implementation sequence, and the provenance links between them.

**Not audited:** the plan's required verification/test sections and required decisions (those are set by the plan's profile or the human, not by this skill); anything the human mandated.

## The Checks

1. **Intent provenance (primary).** Every architecture element traces to a behavioral statement; every behavioral statement traces to a human instruction, pre-existing task text, a verified code/deployed fact, or a recorded simplest-reading assumption. An element with no behavioral line is `invented-requirement`: cut it or convert it to an intent question. A gap filled with the rich reading instead of the simple one is the root defect this skill exists to catch.
2. **Assumption attack.** For each defensive or complex element, name the assumption that creates the need and test whether it is real. Over-engineering is usually downstream of one flawed assumption; kill the assumption and the machinery evaporates.
3. **Existing-construct gate + reinvention police.** Verify every `new` label by searching the target commit, the codebase's shared packages/utilities, and platform features (database constraints, framework/ORM capabilities, managed cloud services, standard library). Reinvention findings cite the existing file path or platform feature; a negative claim ("nothing like this exists") without a cited search is a High `existing-construct` finding.
4. **YAGNI ladder**, per element: does it need to exist → already in the codebase → standard library → platform/framework feature → an already-installed dependency → one line → only then minimum new code. Speculative need is a finding, not a justification.
5. **Convention deviations.** The target project's own conventions and `docs/` rules; established patterns in the surrounding code.

## Worked Examples — Cite These Patterns

**Invented requirement — the admission gate.** Nobody specified what happens to new job requests while a worker is temporarily down. The AI silently answered "reject them" and built a release-gate table plus admission logic. Asked behaviorally — "should new requests queue up and run on recovery, or be rejected?" — any human answers "queue them," and the entire feature evaporates: the durable job row already provided the resilience and every future seam.

**Invented boundary — dual-tracking across your own stores.** Moving data between two of your own databases was pattern-matched to "data crossing a trust boundary," spawning a validation gate and dual-write machinery. Both stores are yours, under your own access control, encrypted, one owner — one boundary, not two. The correct design: move the data, keep one owner.

## Output Contract

Return exactly this block, nothing else:

```md
## Plan Challenge

### Challenges
- High: <element> — <type: stale-baseline | provenance-laundering | invented-requirement | invented-boundary | intent-gap | existing-construct | insufficient-evidence | ladder | reinvention | misclassified-boundary | convention | non-negotiable> — <the assumption attacked, in plain language> — <the simpler alternative, or the question to ask the human> — <evidence that would justify keeping it>
- Medium: ...
- Low: ...

### Verdict
SATISFIED | REVISE — <one sentence>
```

- Severity: **High** = should not exist, reinvents something that exists, or violates a mandatory convention. **Medium** = a simpler alternative exists. **Low** = convention or style.
- Plain language is mandatory: state the concrete behavior first, then name mechanisms.
- "Evidence that would justify keeping it" defines the author's only legitimate rebuttal: a real incident, a measured number, or explicit task text. "Might need it later" never counts.
- No challenges ⇒ `No challenges` and `SATISFIED` with a one-line justification.

## Loop Discipline

- Round caps and stalemate handling live in the calling skill or with the human. On a re-round, examine only what changed and what was rebutted; never reopen settled elements or relitigate a human decision.
- `SATISFIED` applies only to the exact compact plan supplied in that round, with a one-line justification. A material later change needs a fresh challenge of the affected section.
- The challenge record is append-only; attribute every outcome to `challenger`, `human`, or `author/code discovery` — never credit the challenger for a change it did not identify.
