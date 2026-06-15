---
name: closeout
model: sonnet
effort: medium
description: >
  The single exit skill — ends a Bob's thread. Takes a disposition argument
  that selects the exit semantics: `delivered` (happy-path close after a
  merged or landed Premise), `abandoned` (the Premise should not exist
  anymore), `unclaim` (rare; procedural-mistake teardown — the worktree
  should never have existed), `returned` (tried and stopped partway, leave
  a trail for the next agent), or `none` (tear down the worktree without
  touching any Premise). The disposition must be named explicitly;
  `/closeout` with no argument is refused rather than inferred. Every
  disposition archives the worktree and kills the pane; only the
  pre-teardown bookkeeping differs.
---

# Closeout

## Mandatory invocation guard

This skill destroys the worktree and kills the pane. The destruction is asymmetric — a wrongly-invoked closeout cannot be undone within the dying session — so authorisation must be explicit.

**Rule:** proceed only if the operator's most recent typed message contains the literal substring `/closeout` outside of backticks. Synonyms ("close it out", "abandon the premise", "return this", "submit it back") do not count. Backticked references in chat prose (where the operator is naming the skill, not invoking it) do not count. Inferred consent from a generic instruction does not count. The unbackticked slash command, typed by the operator, is the authorisation.

If the most recent typed message does not satisfy the rule, stop here. Reply with a one-line refusal asking the operator to type the slash command themselves, and do not call a transition atom (`vv resolve`, `vv return`, `vv unclaim`) or `vv teardown`, do not transition the Premise, and do not begin any disposition's procedure.

A `PreToolUse` hook (`scaffold/.claude/hooks/check_explicit_invocation.py`, registered in `scaffold/.claude/hooks.json`; on install it is deployed to `~/.claude/hooks/` with the matcher written into `~/.claude/settings.json`) enforces the same rule mechanically. Both layers are intentional; if the hook fires before this prose runs, that is the correct outcome.

## Overview

`/closeout <disposition> --reason "..."` ends the current Bob's thread. Each disposition is a two-step chain: a Premise transition — `vv resolve delivered`, `vv resolve abandoned`, `vv return`, or `vv unclaim` (and `none` skips this) — followed by `vv teardown`, the shared substrate teardown that archives the worktree and kills the tmux pane the same way for every disposition. The transition writes the State + Workflow values and the comment header; the teardown writes nothing to the tracker. The archive captures the worktree body and the Bob's Claude transcript side by side, so the ephemeral session survives alongside the code. Run the transition first and let its failure abort before teardown — once the pane is gone there is no second chance to record the outcome.

BOB splits the lifecycle across two custom fields. State carries the work ladder (`Ready` → `Active` → `Delivered` / `Abandoned`); Workflow carries the pickup-pool marker (`Submitted` / `Claimed` / `Returned`, or empty when the Premise is out of the pool). The disposition argument is the ubiquitous-language outcome term — `delivered` and `abandoned` name State values directly; `returned` names a Workflow value. The fifth bookkeeping disposition, `unclaim`, names a Bob-session outcome ("the worktree should never have existed") rather than a field value: the underlying transition writes `Ready` / `Submitted`, but the operative signal the operator is asking for is "expunge any record this Bob existed," which is a Bob-lifecycle word, not a Premise-lifecycle word.

The skill is the single closeout entry point. It takes exactly one of the five dispositions, named explicitly; there is no inferred default and no router that reads the disposition off session state. Closing out is terminal and pane-destroying, so the disposition is the operator's (or the closing agent's) deliberate choice, never something guessed from PR merge state, working-tree git state, or Premise State/Workflow. `/closeout` with no disposition is refused — see [A disposition is required](#a-disposition-is-required).

## Dispositions

| Disposition | State + Workflow      | Assignee  | Comment header         | When to use |
|-------------|-----------------------|-----------|------------------------|-------------|
| `delivered` | Delivered / (cleared) | kept      | `## Closeout Synopsis` | Premise is done — typically a merged PR, sometimes landed without a PR (tracker-admin, infra-only work). |
| `abandoned` | Abandoned / (cleared) | cleared   | `## Obsolete Reason`   | Premise should not exist anymore — a split replaced it, a duplicate resolved the work elsewhere, the underlying need disappeared. Terminal; `isResolved: true`. |
| `unclaim`   | Ready / Submitted     | cleared   | — (no comment)         | **Rare.** Procedural-mistake teardown — the worktree should never have existed (wrong-Premise spawn, duplicate spawn, operator started a Bob by accident). Equivalent of "expunge any record this even happened." Transition-only: no tracker comment, so a successor picker sees a Premise indistinguishable from one that was never claimed. |
| `returned`  | Active / Returned     | cleared   | `## Return Note`       | Implementation started, hit a wall, and the agent is handing the Premise back with a note the next picker reads before restarting. Unresolved; `vv available` still surfaces it. |
| `none`      | — (unchanged)         | kept      | — (no comment)         | Tear down the worktree and end the thread without touching any Premise. |

## A disposition is required

`/closeout` takes a disposition argument and has no default. Invoked with no argument, refuse: reply with a one-line message naming the five dispositions and asking the operator to pick one, and do not call a transition atom or `vv teardown`, do not transition the Premise, do not infer a disposition from session state. For example: `/closeout needs a disposition — name one of: delivered, abandoned, unclaim, returned, none.`

A bare `/closeout` is the operator reaching for the skill before naming the outcome. The teardown is terminal and pane-destroying — too expensive to get wrong to hang on a guess — and naming the disposition is cheap to type. The five are `delivered`, `abandoned`, `unclaim`, `returned`, and `none`; each names a distinct lifecycle outcome, and the operator or the closing agent picks the one that fits.

## Procedure per disposition

The `delivered` disposition has a multi-step body because the happy path needs to decide whether the Premise has a PR, a retroactive Premise, or neither. `abandoned` and `returned` are thin: gather a one-line reason, print it to chat, run the transition atom, then `vv teardown`. `unclaim` is thinner still — print a one-line chat note for the operator scrolling the dying pane, run `vv unclaim` (no reason; it leaves no tracker record by design), then `vv teardown`. `none` skips the transition entirely and runs only `vv teardown`. Every disposition ends with the detached teardown — once launched, the pane (and this agent) die shortly after.

### `delivered`

Happy-path close after a completed Premise. Captures what happened — how the implementation lined up with the Premise as written — as a permanent record on the tracker, then marks the Premise done.

#### Step 0: Determine the closeout path

Three paths are possible, and this step picks one before any other work. The dispatch table:

|                       | Has merged PR    | No merged PR             |
|-----------------------|------------------|--------------------------|
| **Has Premise ID**       | PR path (Step 1) | no-PR path (Step 1c)     |
| **No Premise ID**        | ad-hoc (Step 1b) | nothing to close — stop  |

##### 0a. Try to find the Premise's PR

The goal is to determine whether a PR exists **for the Premise being closed out** — not whether the current branch happens to have one. `/closeout delivered` can be invoked from any worktree; the branch is incidental. Conflating "PR on this branch" with "PR for this Premise" produces two failure modes: an unrelated open PR on the branch stops a legitimate no-PR closeout, and an unrelated merged PR on the branch routes the skill to the wrong PR.

Do not assume merge status from conversation context or the user's invocation; check GitHub directly.

**If a Premise ID is known** (from `$ARGUMENTS` or the conversation context), look up the PR by Premise ID — the Premise is the identity, the branch is not:

```bash
gh pr list --state all --search "<PREMISE> in:title" --json number,title,state,mergedAt,url
```

- One **merged** PR → that is the Premise's PR; continue to 0b (PR path).
- One **open** PR → the Premise's PR exists but has not been merged. Report status and stop; `/closeout delivered` requires a merged PR.
- **No result** → the Premise may have landed without a PR. Continue to 0b (no-PR path).
- Multiple results → rare; inspect titles, pick the one matching the Premise's scope, or ask the operator.

**If no Premise ID is known** (ad-hoc closeout with no prior Premise), the PR is most likely on the current branch or was named in the invocation:

```bash
# If a PR number or URL was passed in $ARGUMENTS or mentioned in the conversation
gh pr view <number-or-url> --json state,mergedAt,number,title

# Otherwise, the current branch (the likely location of ad-hoc work)
gh pr view --json state,mergedAt,number,title

# Final fallback — recent merged PRs, pick the one matching the work under discussion
gh pr list --state merged --limit 10 --json number,title,mergedAt,headRefName,author
```

- Merged PR resolved → continue to 0b (ad-hoc path).
- Open PR resolved (and it's the PR the caller wants to close out) → report status and stop.
- Nothing found → 0b dispatches to "nothing to close out".

If the ladder returns ambiguity, ask the operator rather than guessing. Only after every step comes up empty may you conclude "no PR exists" — a PR lookup that merely didn't find the PR on the first try is not the same thing as a Premise that was completed without a PR.

##### 0b. Dispatch

- **Merged PR found**:
  - Premise ID is known → PR path. Continue to **0c**, then **Step 1**.
  - No Premise ID → ad-hoc. Continue to **Step 1b**.
- **No merged PR exists** (after fully exhausting the ladder above):
  - Premise ID is known → no-PR path. Continue to **0c**, then **Step 1c**.
  - No Premise ID → nothing to close out. Stop and report to the operator; the agent should not invent a Premise to document ad-hoc work that produced no artifact.

##### 0c. Offer `/onward` when the Premise has dependents

Before gathering context, check whether other Premises depend on this one — `vv premise-show <PREMISE>` lists them under `deps_outward`. If any do, name the choice and let the operator pick: `/onward` closes *and* spawns a Bob on each peer the close unblocks, where `/closeout delivered` closes without fanout. The operator forgets `/onward` reflexively, so surface it, then wait — closeout can't invoke `/onward` itself, and re-offering after they answer `/closeout delivered` only nags, so offer once. Don't filter `deps_outward` for which peers are actually pickable; `/onward` handles that and no-ops if none are. On an empty `deps_outward`, or the ad-hoc path (a retroactive Premise has no dependents), say nothing and continue.

#### Step 1: Gather Context (PR path)

1. Fetch the Premise description from the tracker using the Premise ID from `$ARGUMENTS` or the conversation context.
2. Read the merged PR (diff, description, review comments).
3. Review the conversation history for key decisions, plan deviations, and domain learnings.

Continue to Step 2.

#### Step 1b: Create a Retroactive Premise (ad-hoc path)

Work sometimes lands without a tracker Premise — ad hoc fixes, requests that didn't warrant upfront planning, work that grew from a quick question into a PR. The closeout still needs a home in the tracker so the institutional record is complete.

1. Read the merged PR (diff, description, review comments).
2. Review the conversation history for what was done and why.
3. Create the Premise with a summary and description derived from the actual work — not boilerplate. The description should note that this is a retroactive Premise and briefly explain what prompted the work. `vv premise-create` writes into the project whose main clone contains cwd; Type, Route, and Workflow are required project fields, so the call must set all three (Type defaults to `Premise` and Workflow defaults to `Submitted`).
   ```bash
   new_id=$(vv premise-create \
     --summary "..." \
     --description "..." \
     --route check-in)
   ```

Continue to Step 2 with the newly created Premise ID.

#### Step 1c: Gather Context (no-PR path)

Some Premises land entirely outside git — tracker-admin changes, third-party config, infra-only work whose artifacts live in another system's state rather than in a diff. The Premise still needs a closeout; there is just no PR to read.

1. Fetch the Premise description from the tracker using the Premise ID from `$ARGUMENTS` or the conversation context.
2. Review the conversation history for what was done: which API calls ran, what responses came back, what decisions were made, what deviated from the Premise as written.
3. Gather whatever API-response evidence the agent captured (command outputs, response bodies, state changes observed in the target system). This is the substitute for the PR diff — thin, but it is what actually happened.

The synopsis in Step 2 must ground in these three sources. Do **not** write a pre-PR narrative that invents a code change that did not exist, and do not paper over the no-PR-ness by paraphrasing the Premise description back as if it were an implementation report.

Continue to Step 2.

#### Step 2: Write the Synopsis

Draft a comment for the Premise. The comment MUST begin with the header `## Closeout Synopsis` — this allows a future agent to identify it programmatically among other discussion comments.

The synopsis answers three questions:

**What was built vs. what was planned?**
- Did the implementation track the Premise.s framing?
- Was anything added, dropped, or descoped? Why?
- Were there significant departures from the plan? What drove them?

**What did we learn in the course of the work?**
- Did the implementation reveal anything the Premise didn't anticipate?
- Any surprises about the existing code, the tooling, or the adjacent skills?

**What should downstream Premises know?**
- Decisions that constrain or enable future work.
- Patterns established that subsequent Premises should follow (or avoid).
- Anything a future agent would waste time rediscovering without this note.

Keep the comment concise — a future agent skimming the history should be able to read it in under a minute. Use bullet points. No preamble or pleasantries.

#### Step 3: Brief Output

Report to the operator:
- Premise ID and final state
- One-line summary of the synopsis posted
- Any downstream concerns flagged in the comment

This is the agent's last opportunity to communicate, because Step 4 destroys the pane the agent is running in. Print the report, then proceed.

#### Step 4: Transition, then tear down

Chain the two atoms. `vv resolve delivered` posts the `## Closeout Synopsis` comment and transitions State to `Delivered`; `vv teardown` then launches the detached worktree archive + `workmux remove --force` teardown. Run the resolve first and abort on its failure — a failed transition must not fall through to a teardown that erases the only record of the outcome. Once teardown launches, the pane (and this agent) die shortly after.

```bash
vv resolve delivered <PREMISE> --reason "$SYNOPSIS" || {
  echo "resolve failed; Premise not transitioned, worktree left intact" >&2; exit 1;
}
vv teardown
```

`$SYNOPSIS` is the comment body assembled in Step 2 (the `## Closeout Synopsis` header is added automatically). Progress and errors from the detached teardown land in `/tmp/teardown-archive.log` for post-mortem inspection.

### `abandoned`

The Premise is structurally stale — a duplicate has been resolved, a split conversation has replaced the parent with child Premises, or the underlying need disappeared. The terminal State (resolved) signals to future queries (and `vv available`) that this Premise should never be picked up again.

**Not** `returned` (the work is valid but was attempted and stopped) and **not** `unclaim` (procedural-mistake teardown — the Premise itself is fine, the spawn was wrong; here the Premise itself is the problem).

#### Step 1: Print the reason to chat

Last chance to communicate. State the Premise ID and the one-line reason (e.g. `VV-117 abandoned — split into VV-154, VV-155, VV-156, VV-157`).

#### Step 2: Transition, then tear down

```bash
vv resolve abandoned <PREMISE> --reason "$REASON" || {
  echo "resolve failed; Premise not transitioned, worktree left intact" >&2; exit 1;
}
vv teardown
```

`vv resolve abandoned` posts an `## Obsolete Reason` comment, transitions State to `Abandoned` and clears Workflow, and clears Assignee; `vv teardown` then launches the detached teardown. Progress lands in `/tmp/teardown-archive.log`.

### `unclaim`

**Rare.** Procedural-mistake teardown: the worktree should never have been started in the first place. A spawn fired on the wrong Premise, a duplicate spawn collided with one already in flight, an operator started a Bob by accident. The State/Workflow transition (`Ready` / `Submitted`) and the cleared Assignee leave the Premise indistinguishable from one that was never picked up; the disposition is the equivalent of "expunge any record this even happened."

The name is the Bob-session word for the action — the operator is *unclaiming* a Premise that should never have been claimed. The underlying Workflow value is still `Submitted` (the pickup-pool marker the Premise reverts to), but the disposition argument names the operator's intent rather than the field value because the Workflow term `Submitted` doesn't capture "this Bob shouldn't have existed."

**The disposition is comment-free.** Unlike the other transition atoms, `vv unclaim` writes the field transition without posting a tracker comment — there is no `## Unclaim Reason` header, no body, nothing the next picker will see. A "whoops" comment would defeat the entire purpose of the disposition by handing a successor a distracting artifact to read past. The chat line below is for the operator's own scrollback in the dying pane; it never reaches anyone else. `vv unclaim` takes no `--reason` — it has no comment to attach one to.

**Not** `returned` (which implies work was attempted and stopped — actively misleading when the right semantic is "this Bob shouldn't have existed") and **not** `abandoned` (which marks the Premise itself terminally invalid; here the Premise is fine, the spawn was wrong).

A dep-blocked Premise is **not** an `unclaim` case — `vv spawn-preflight` refuses dep-blocked Premises upstream of `workmux add`, so a Bob never spawns on one in the first place. `unclaim` is reserved for the procedural-mistake case where a Bob did spawn and the teardown is the intent. It requires an explicit human (or operator) judgement that the Bob had no right to exist.

#### Step 1: Print a one-line note to chat

For the operator scrolling the dying pane only — this is not the durable record. State the Premise ID and what happened (e.g. `BOB-201 unclaimed — duplicate spawn, original Bob already in flight on bob-37`).

#### Step 2: Transition, then tear down

```bash
vv unclaim <PREMISE> || {
  echo "unclaim failed; Premise not transitioned, worktree left intact" >&2; exit 1;
}
vv teardown
```

No `--reason` — the disposition does not write a comment. `vv unclaim` transitions State to `Ready` and Workflow to `Submitted` (idempotent if already in that pair) and clears Assignee; `vv teardown` then launches the detached teardown. The Premise re-enters `vv available`'s candidate set on the next run.

### `returned`

Implementation started, hit something that stops it — an AC is wrong, the approach doesn't work, a hidden constraint surfaced, the operator's guidance is needed but the Bob can't wait — and the agent is handing the Premise back rather than shipping. The Returned state is a signal to the next agent: *someone has been here; read the comment before you start.*

**Not** `unclaim` (which means the Bob shouldn't have existed at all — a procedural mistake, no trail to leave) and **not** `abandoned` (use when the Premise itself is terminally wrong).

#### Step 1: Print the note to chat

Last chance to communicate. State the Premise ID and a one-line summary of what was tried and why the agent stopped (e.g. `<PREMISE> returned — tried approach X; AC 3 conflicts with Y; needs guidance on Z`). The full note lands in the tracker comment.

#### Step 2: Transition, then tear down

```bash
vv return <PREMISE> --reason "$NOTE" || {
  echo "return failed; Premise not transitioned, worktree left intact" >&2; exit 1;
}
vv teardown
```

`vv return` posts a `## Return Note` comment (the header is the anchor the next agent looks for), transitions State to `Active` and Workflow to `Returned` (unresolved, `vv available` still surfaces it), and clears Assignee; `vv teardown` then launches the detached teardown.

### `none`

Tear down the worktree and archive the session without touching any Premise — the plain teardown, no additional machinery. No transition atom runs and nothing reaches the tracker; the agent simply goes away. Use it when the pane should die and there is no tracker write to make.

**Not** `unclaim`. The two are categorically different, not adjacent: `unclaim` is a tracker transition — it clears the assignee and returns the Premise to the pickup pool so a successor finds it as if untouched — while `none` touches the tracker not at all. Reach for `unclaim` when a Premise should go back to the pool; reach for `none` when the only thing that should happen is the session ending.

#### Step 1: Print a brief reason to chat

Last chance to communicate. State why the thread is ending — there is no Premise comment to capture it, so the chat line is the only record.

#### Step 2: Tear down

```bash
vv teardown
```

No transition atom runs — `none` skips the comment + field-transition + Assignee bookkeeping entirely. `vv teardown` launches only the detached worktree archive + `workmux remove --force` teardown.
