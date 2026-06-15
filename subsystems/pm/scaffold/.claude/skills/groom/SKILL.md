---
name: groom
description: >
  Comprehensive backlog-wide drift scan using parallel audit agents — one per
  project. Finds judgment-grade drift (stale framing, dead Depend edges,
  description drift, returned-without-followup, right-idea-wrong-shape) that
  mechanical detectors miss. Applies obvious DELIVERED/ABANDONED closeouts
  inline; presents a punch list keyed by Premise ID for everything that needs
  operator adjudication.
---

# Groom

`/groom` is the primary drift-detection tool for the backlog. It dispatches one audit agent per project in parallel; each agent reads its project's backlog and code, then classifies every unresolved Premise. Obvious DELIVERED/ABANDONED findings are applied inline. The remainder surfaces as a punch list the operator adjudicates.

## Division of responsibility

- **`/groom`** (this skill) — comprehensive. Runs intermittently over the whole non-resolved backlog across all projects under PM management. Catches judgment-grade drift the narrow pickable-candidate pass cannot.
- **`/available`** — narrow. Grooms only the candidate set it is about to recommend spawning. For comprehensive backlog-wide drift detection, invoke `/groom`.

## Procedure

### Step 1 — Pull the unresolved-Premise inventory per project

For each project under PM management (BOB, CORE, CUE, HOOK, PM, RING), use the YouTrack API to fetch every unresolved Premise. Credentials live in `~/.vaudeville/credentials.toml` (same path as `vv available`).

Per project, fetch: id, summary, type, state, workflow, route, description (full body), Depend edges (inward and outward), Duplicate link relations (both "is duplicate of" and "duplicated by").

One API call per project. Record the result as the inventory for that project.

### Step 2 — Dispatch one audit agent per project in parallel

Spawn one agent per project. Each agent receives:

- **Project shortName** and its **repo path on disk** (resolve via `vv spawn-target-repo <project>` or the known clone layout under `~/vaudeville-*`).
- **The Ticket inventory** for its project (from Step 1).
- **Recent context**: last ~20 commits (`git log --oneline -20`) from the project's repo, and any recently resolved Premises visible in the API (last 2 weeks).
- **The classification rubric** (see Step 3).

Agents run in parallel.

### Step 3 — Each agent reads its backlog and code

Each agent inspects its project's inventory against the repo. For every unresolved Premise, the agent classifies it as exactly one of:

| Classification | Meaning | Required evidence |
|---|---|---|
| `DELIVERED` | The deliverable is already in the code. | `file:line` citation — a specific location in the repo where the deliverable lives. |
| `ABANDONED` | The Premise should not exist. | A reason: superseded by another Premise, misfiled, the need dissolved. Cite the superseding Premise ID if applicable. |
| `PUNCH-LIST` | Judgment-grade staleness the operator must adjudicate. | What is stale: stale framing, description drift (e.g. parentheticals like "(Delivered)" that aren't accurate), returned-without-followup, right-idea-wrong-shape, Depend edge pointing at a silently-abandoned Premise, Depend edge pointing at a Premise marked as Duplicate (should be rerouted to the canonical Premise). |
| `KEEP` | No drift detected; backlog is healthy for this Premise. | None required. |

Agents return a structured list of findings: `{premise_id, classification, evidence, note}`.

### Step 4 — Aggregate and apply

**Inline apply — no confirmation needed** for findings with hard evidence:

- `DELIVERED` with a `file:line` citation: call `vv resolve delivered <PREMISE> --reason "<note>"`.
- `ABANDONED` with a clear reason: call `vv resolve abandoned <PREMISE> --reason "<note>"`.
- Minor description-staleness (a parenthetical that is simply wrong, a one-line correction): call `vv comment-add <PREMISE> --body "<correction>"`.

**Do not inline-apply** when the evidence is circumstantial (no `file:line` for DELIVERED; no clear superseding Premise for ABANDONED). Those go on the punch list.

Refresh the inventory after inline applies so the punch list reflects the post-apply state.

### Step 5 — Present the punch list

For each remaining PUNCH-LIST item, output:

1. **`<PREMISE>`** — one-line plain-English description of what this Premise is.
2. **What's stale** — the specific drift this agent observed.
3. **Concrete options** — two or three credible options (e.g. `ABANDONED`, `DELIVERED`, close as wont-do, reframe).
4. **Your take** — commit to a recommendation. The operator adjudicates.

Number paragraphs hierarchically (**1.1**, **1.2**, …) when the list is long enough that the operator may respond paragraph-by-paragraph via `/tmp`.

End with a one-line summary: "Applied M closeouts inline; N items on the punch list awaiting your call."

## Output shape

```
## Grooming run — <date>

### Inline applied (M)
- <PREMISE>: DELIVERED — <reason> (<file:line>)
- <PREMISE>: ABANDONED — <reason>

### Punch list (N)

**1. <PREMISE>** — <one-line description>
Stale: <what the agent observed>
Options: (a) ABANDONED — <why; (b) DELIVERED — <why; (c) reframe — <how>
Take: (a) — <reasoning>

**2. <PREMISE>** — …
```

## Credentials

The YouTrack API credentials live in `~/.vaudeville/credentials.toml`. If an API call fails with a credentials error, verify the token there before retrying.

## Non-goals

- **Not a spawn recommender.** Premise selection for spawning is `/available`'s job.
- **Not a silent auto-fixer.** Only findings with hard `file:line` or clear-reason evidence are applied inline. Everything else is a punch-list proposal.
- **Not a substitute for `/available`.** `/available` runs its own narrower grooming pass as a backstop before recommending Premises to spawn. `/groom` is the intermittent comprehensive pass; the two are complementary.
