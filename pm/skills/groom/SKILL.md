---
name: groom
description: >
  Comprehensive backlog-wide drift scan using parallel audit agents, one per
  Component. Finds judgment-grade drift (stale framing, dead Depend edges,
  description drift, returned-without-followup, right-idea-wrong-shape) that
  mechanical detectors miss. Applies obvious DELIVERED/ABANDONED closeouts
  inline; presents a punch list keyed by Assignment ID for everything that needs
  operator adjudication.
---

# Groom

`/groom` is the primary drift-detection tool for the backlog. It dispatches one audit agent per Component in parallel; each agent reads its Component's backlog and code, then classifies every unresolved Assignment. Obvious DELIVERED/ABANDONED findings are applied inline. The remainder surfaces as a punch list the operator adjudicates.

## Division of responsibility

- **`/groom`** (this skill): comprehensive. Runs intermittently over the whole non-resolved backlog across all Components under PM management. Catches judgment-grade drift the narrow pickable-candidate pass cannot.
- **`/available`**: narrow. Grooms only the candidate set it is about to recommend spawning. For comprehensive backlog-wide drift detection, invoke `/groom`.

## Procedure

### Step 1: Pull the unresolved-Assignment inventory per Component

For each Component under PM management (BOB, CORE, CUE, HOOK, PM, RING), use the YouTrack API to fetch every unresolved Assignment. Credentials live in `~/.vaudeville/credentials.toml` (same path as `vv available`).

Per Component, fetch: id, summary, type, state, workflow, route, description (full body), Depend edges (inward and outward), Duplicate link relations (both "is duplicate of" and "duplicated by").

One API call per Component. Record the result as the inventory for that Component.

### Step 2: Dispatch one audit agent per Component in parallel

Spawn one agent per Component. Each agent receives:

- **Component shortName** and its **repo path on disk** (resolve via `vv spawn-target-repo <project>` or the known clone layout under `~/vaudeville-*`).
- **The Ticket inventory** for its Component (from Step 1).
- **Recent context**: last ~20 commits (`git log --oneline -20`) from the Component's repo, and any recently resolved Assignments visible in the API (last 2 weeks).
- **The classification rubric** (see Step 3).

Agents run in parallel.

### Step 3: Each agent reads its backlog and code

Each agent inspects its Component's inventory against the repo. For every unresolved Assignment, the agent classifies it as exactly one of:

| Classification | Meaning | Required evidence |
|---|---|---|
| `DELIVERED` | The deliverable is already in the code. | `file:line` citation: a specific location in the repo where the deliverable lives. |
| `ABANDONED` | The Assignment should not exist. | A reason: superseded by another Assignment, misfiled, the need dissolved. Cite the superseding Assignment ID if applicable. |
| `PUNCH-LIST` | Judgment-grade staleness the operator must adjudicate. | What is stale: stale framing, description drift (e.g. parentheticals like "(Delivered)" that aren't accurate), returned-without-followup, right-idea-wrong-shape, Depend edge pointing at a silently-abandoned Assignment, Depend edge pointing at an Assignment marked as Duplicate (should be rerouted to the canonical Assignment). |
| `KEEP` | No drift detected; backlog is healthy for this Assignment. | None required. |

Agents return a structured list of findings: `{assignment_id, classification, evidence, note}`.

### Step 4: Aggregate and apply

**Inline apply, no confirmation needed** for findings with hard evidence:

- `DELIVERED` with a `file:line` citation: call `vv resolve delivered <ASSIGNMENT> --reason "<note>"`.
- `ABANDONED` with a clear reason: call `vv resolve abandoned <ASSIGNMENT> --reason "<note>"`.
- Minor description-staleness (a parenthetical that is simply wrong, a one-line correction): call `vv comment-add <ASSIGNMENT> --body "<correction>"`.

**Do not inline-apply** when the evidence is circumstantial (no `file:line` for DELIVERED; no clear superseding Assignment for ABANDONED). Those go on the punch list.

Refresh the inventory after inline applies so the punch list reflects the post-apply state.

### Step 5: Present the punch list

For each remaining PUNCH-LIST item, output:

1. **`<ASSIGNMENT>`**: one-line plain-English description of what this Assignment is.
2. **What's stale**: the specific drift this agent observed.
3. **Concrete options**: two or three credible options (e.g. `ABANDONED`, `DELIVERED`, close as wont-do, reframe).
4. **Your take**: commit to a recommendation. The operator adjudicates.

Number paragraphs hierarchically (**1.1**, **1.2**, …) when the list is long enough that the operator may respond paragraph-by-paragraph via `/tmp`.

End with a one-line summary: "Applied M closeouts inline; N items on the punch list awaiting your call."

## Output shape

```
## Grooming run: <date>

### Inline applied (M)
- <ASSIGNMENT>: DELIVERED: <reason> (<file:line>)
- <ASSIGNMENT>: ABANDONED: <reason>

### Punch list (N)

**1. <ASSIGNMENT>**: <one-line description>
Stale: <what the agent observed>
Options: (a) ABANDONED, <why; (b) DELIVERED, <why; (c) reframe, <how>
Take: (a), <reasoning>

**2. <ASSIGNMENT>**: …
```

## Credentials

The YouTrack API credentials live in `~/.vaudeville/credentials.toml`. If an API call fails with a credentials error, verify the token there before retrying.

## Non-goals

- **Not a spawn recommender.** Assignment selection for spawning is `/available`'s job.
- **Not a silent auto-fixer.** Only findings with hard `file:line` or clear-reason evidence are applied inline. Everything else is a punch-list proposal.
- **Not a substitute for `/available`.** `/available` runs its own narrower grooming pass as a backstop before recommending Assignments to spawn. `/groom` is the intermittent comprehensive pass; the two are complementary.
