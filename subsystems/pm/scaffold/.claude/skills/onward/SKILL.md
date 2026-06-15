---
name: onward
description: >
  Close-and-saturate skill. A superset of `/closeout delivered` that spawns a
  Bob on every Premise newly unblocked by this close before tearing down.
  Use for the happy-path close when you want dependency-graph follow-through
  — the common case. Use `/closeout delivered` when you explicitly do not want
  fanout (a retroactive close whose downstream peers were authored without
  this close in mind, or any case where the Bob should control what spawns
  by hand).
model: sonnet
effort: medium
---

# Onward

## Mandatory invocation guard

This skill destroys the worktree and kills the pane after fanning out. The destruction is asymmetric — a wrongly-invoked onward cannot be undone within the dying session — so authorisation must be explicit.

**Rule:** proceed only if the operator's most recent typed message contains the literal substring `/onward` outside of backticks. Synonyms ("close and saturate", "fan out from this", "close it out and spawn the peers") do not count. Backticked references in chat prose (where the operator is naming the skill, not invoking it) do not count. Inferred consent from a generic instruction does not count. The unbackticked slash command, typed by the operator, is the authorisation.

If the most recent typed message does not satisfy the rule, stop here. Reply with a one-line refusal asking the operator to type the slash command themselves, and do not call `vv resolve delivered`, `vv unblocked`, or `vv teardown`, do not transition the Premise, and do not begin the spawn fanout.

A `PreToolUse` hook (`.claude/hooks/check_explicit_invocation.py`, registered in `.claude/settings.json`) enforces the same rule mechanically. Both layers are intentional; if the hook fires before this prose runs, that is the correct outcome.

## Overview

`/onward <PREMISE>` closes a Premise with the `delivered` disposition, spawns a Bob on every Premise the close newly unblocked, and tears down. The skill is the one-command path for the saturation goal: don't make the Bob run `/available` after every close to figure out what opened up — the graph already knows.

"Newly unblocked" is defined exactly like `/available`'s predicate: Workflow `Submitted` or `Returned`, Type `Premise`, every inward `Depend` peer resolved (State `isResolved: true` — `Delivered` or `Abandoned`). The candidate set is scoped narrowly to the just-delivered Premise's outward `Depend` peers (the Premises that required this one), not the whole backlog — drift elsewhere remains `/groom`'s problem.

`/closeout delivered` is preserved as its current behavior. Use it when you explicitly do not want fanout.

## Procedure

### Step 0: Determine the closeout path

Three paths are possible, and this step picks one before any other work. The dispatch table:

|                       | Has merged PR    | No merged PR             |
|-----------------------|------------------|--------------------------|
| **Has Premise ID**       | PR path (Step 1) | no-PR path (Step 1c)     |
| **No Premise ID**        | ad-hoc (Step 1b) | nothing to close — stop  |

##### 0a. Try to find the Premise's PR

The goal is to determine whether a PR exists **for the Premise being closed out** — not whether the current branch happens to have one. `/onward` can be invoked from any worktree; the branch is incidental. Conflating "PR on this branch" with "PR for this Premise" produces two failure modes: an unrelated open PR on the branch stops a legitimate no-PR closeout, and an unrelated merged PR on the branch routes the skill to the wrong PR.

Do not assume merge status from conversation context or the user's invocation; check GitHub directly.

**If a Premise ID is known** (from `$ARGUMENTS` or the conversation context), look up the PR by Premise ID — the Premise is the identity, the branch is not:

```bash
gh pr list --state all --search "<PREMISE> in:title" --json number,title,state,mergedAt,url
```

- One **merged** PR → that is the Premise's PR; continue to 0b (PR path).
- One **open** PR → the Premise's PR exists but has not been merged. Report status and stop; `/onward` requires a merged PR.
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
  - Premise ID is known → PR path. Continue to **Step 1**.
  - No Premise ID → ad-hoc. Continue to **Step 1b**.
- **No merged PR exists** (after fully exhausting the ladder above):
  - Premise ID is known → no-PR path. Continue to **Step 1c**.
  - No Premise ID → nothing to close out. Stop and report to the operator; the agent should not invent a Premise to document ad-hoc work that produced no artifact.

### Step 1: Gather Context (PR path)

1. Fetch the Premise description from the tracker using the Premise ID from `$ARGUMENTS` or the conversation context.
2. Read the merged PR (diff, description, review comments).
3. Review the conversation history for key decisions, plan deviations, and domain learnings.

Continue to Step 2.

### Step 1b: Create a Retroactive Premise (ad-hoc path)

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

### Step 1c: Gather Context (no-PR path)

Some Premises land entirely outside git — tracker-admin changes, third-party config, infra-only work whose artifacts live in another system's state rather than in a diff. The Premise still needs a closeout; there is just no PR to read.

1. Fetch the Premise description from the tracker using the Premise ID from `$ARGUMENTS` or the conversation context.
2. Review the conversation history for what was done: which API calls ran, what responses came back, what decisions were made, what deviated from the Premise as written.
3. Gather whatever API-response evidence the agent captured (command outputs, response bodies, state changes observed in the target system). This is the substitute for the PR diff — thin, but it is what actually happened.

The synopsis in Step 2 must ground in these three sources. Do **not** write a pre-PR narrative that invents a code change that did not exist, and do not paper over the no-PR-ness by paraphrasing the Premise description back as if it were an implementation report.

Continue to Step 2.

### Step 2: Write the Synopsis

Draft a comment for the Premise. The comment MUST begin with the header `## Closeout Synopsis` — this allows a future agent to identify it programmatically among other discussion comments.

The synopsis answers three questions:

**What was built vs. what was framed?**
- Did the implementation track the Premise's framing? Where it diverged, why?
- Was anything added, dropped, or descoped? Why?
- Were there significant departures from the prep's working plan? What drove them?

**What did we learn in the course of the work?**
- Did the implementation reveal anything the Premise didn't anticipate?
- Any surprises about the existing code, the tooling, or the adjacent skills?

**What should downstream Premises know?**
- Decisions that constrain or enable future work.
- Patterns established that subsequent Premises should follow (or avoid).
- Anything a future agent would waste time rediscovering without this note.

Keep the comment concise — a future agent skimming the history should be able to read it in under a minute. Use bullet points. No preamble or pleasantries.

### Step 3: Brief Output

Report to the operator:
- Premise ID and final state
- One-line summary of the synopsis posted
- Any downstream concerns flagged in the comment
- Note that fanout (Step 5) will also post per-spawn reports to chat, but this Step 3 report is the authoritative end-of-Bob summary

This is the agent's last opportunity to own the close narrative. Subsequent spawn reports arrive one per peer; they are the new Bobs announcing themselves, not this one. Print the report, then proceed.

### Step 4: Bookkeep and identify unblocked peers

Hand off the tracker side of the close, and collect the ids of peers this close just freed up:

```bash
vv resolve delivered <PREMISE> --reason "$SYNOPSIS" || { echo "resolve failed; aborting /onward before fanout" >&2; exit 1; }
peers=$(vv unblocked <PREMISE>)
printf '%s\n' "$peers"   # surface the captured list to chat for recovery
```

`vv resolve delivered` posts the `## Closeout Synopsis` comment and transitions State to `Delivered`; `vv unblocked` then prints the newly-pickable peer ids to stdout — one id per line, sorted, with no other chatter — and refuses only if the Premise is somehow not resolved, which `vv resolve delivered` just guaranteed. The `|| exit 1` on the resolve is load-bearing: a failed bookkeeping must abort the close loudly, not fall through to a fanout that would then look empty. `$peers` carries the list into Step 5's loop; the `printf` ensures the same list lands in chat as a visible audit trail, since the recovery guidance later (in Tips) keys off "the printed ids." Neither command launches teardown — sequencing is this skill's job.

### Step 5: Spawn a Bob per unblocked peer

For each `<peer>` id printed in Step 4, run `vv spawn` — once per id, in a bash loop:

```bash
for peer in $peers; do
  vv spawn "$peer" || continue
done
```

`vv spawn` is the canonical composed spawn: it preflights the peer, resets the managed clones, forks the peer Managed Repository's Foundation, pre-seeds the worktree's folder-trust, and runs `workmux add --background` in the peer's own target repo with the Bob's full agent command (auto-mode permissions, the scaffold env trio, Remote Control). Running it per peer is what makes the fanout cross-project: each peer spawns into the repo its prefix names, not `/onward`'s repo.

The `|| continue` is the fanout's fault tolerance, and it is load-bearing under two `/onward` closes running concurrently on the same newly-unblocked peer. `vv spawn`'s internal preflight refuses a peer another close already claimed (Workflow `Claimed`, or State resolved), exiting non-zero so `continue` skips it and the loop proceeds. If both closes race past preflight before either Bob has claimed, `vv spawn`'s `workmux add` refuses the second on the canonical `<prefix>-<n>` worktree-name collision — also non-zero, also skipped. Either guard catches the race with no coordination, and stderr from each `vv spawn` surfaces directly to chat.

Post a one-line report per successfully-spawned peer (Premise id and the `wm open <prefix>-N` command, where the worktree is `vv spawn`'s canonical `<lowercase-prefix>-<number>` — e.g. `pm-40`, no `bob-` prefix). If the unblocked list is empty, this step is a no-op.

### Step 6: Teardown

Run the bare detached teardown:

```bash
vv teardown
```

This archives the worktree and kills the pane. `vv teardown` writes nothing to the tracker — the transition already happened in Step 4's `vv resolve delivered`, so there is nothing left to record.

## Tips

- **Saturation is the default, not a side effect.** If the fanout is empty, the Premise genuinely had no downstream peers waiting on it; that is fine. If the fanout is non-empty, those peers were already waiting — `/onward` is not creating work, it is surfacing work that was held behind this close.

- **Concurrent closes are safe by construction.** Two `/onward` closes that both see the same newly-unblocked peer will both try to spawn on it. `vv spawn`'s internal preflight refuses claimed/resolved Premises (Workflow `Claimed` or State `isResolved: true`), and its `workmux add` refuses a canonical-worktree-name collision. Either guard catches the race; you don't need to coordinate.

- **Recovery from mid-flight interruption is manual.** `/onward` is not resumable. If Step 4 succeeded (Premise is `Delivered`) but Step 5 was interrupted mid-loop, finish the spawns by hand from the printed ids — re-running `vv spawn` per remaining peer, or invoking `/spawn` once per peer — then run `/closeout none` to tear down. Do not re-run `/onward` on the same Premise; re-running `vv resolve delivered` would duplicate the synopsis comment.

- **Use `/closeout delivered` when you want to opt out.** A retroactive close (Step 1b) whose downstream peers were authored without this close in mind, or any close where the Bob wants to hand-pick what spawns, should use `/closeout delivered` directly.
