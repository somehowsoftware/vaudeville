---
name: onward
description: >
  Close-and-saturate skill. A superset of `/closeout delivered` that spawns a
  Bob on every Assignment newly unblocked by this close before tearing down.
  Use for the happy-path close when you want dependency-graph follow-through,
  the common case. Use `/closeout delivered` when you explicitly do not want
  fanout (a retroactive close whose downstream peers were authored without
  this close in mind, or any case where the Bob should control what spawns
  by hand).
model: opus
effort: medium
---

# Onward

## Mandatory invocation guard

This skill destroys the worktree and kills the pane after fanning out. The destruction is asymmetric (a wrongly-invoked onward cannot be undone within the dying session) so authorisation must be explicit.

**Rule:** proceed only if the operator's most recent typed message contains the literal substring `/onward` outside of backticks. Synonyms ("close and saturate", "fan out from this", "close it out and spawn the peers") do not count. Backticked references in chat prose (where the operator is naming the skill, not invoking it) do not count. Inferred consent from a generic instruction does not count. The unbackticked slash command, typed by the operator, is the authorisation.

If the most recent typed message does not satisfy the rule, stop here. Reply with a one-line refusal asking the operator to type the slash command themselves, and do not call `vv resolve delivered`, `vv unblocked`, or `vv teardown`, do not transition the Assignment, and do not begin the spawn fanout.

A `PreToolUse` hook (`.claude/hooks/check_explicit_invocation.py`, registered in `.claude/settings.json`) enforces the same rule mechanically. Both layers are intentional; if the hook fires before this prose runs, that is the correct outcome.

## Overview

`/onward <ASSIGNMENT>` closes an Assignment with the `delivered` disposition, spawns a Bob on every Assignment the close newly unblocked, and tears down. The skill is the one-command path for the saturation goal: don't make the Bob run `/available` after every close to figure out what opened up; the graph already knows.

A close can also free a Command or Manual the operator has not yet signed off. The fanout does not spawn these: operator-authored work enters the pool only on sign-off, so the close surfaces it for the operator's decision instead of letting it stall unseen. A signed-off Command or Manual is already in the pool and spawns like any other peer.

"Newly unblocked" means **pickable** (the rule `/available` draws on): Workflow `Submitted` or `Returned`, every inward `Depend` peer resolved, the kind cleared for the pool. The candidate set is scoped to the just-delivered Assignment's outward `Depend` peers (the Assignments that required this one), not the whole backlog; drift elsewhere remains `/groom`'s problem.

`/closeout delivered` is preserved as its current behavior. Use it when you explicitly do not want fanout.

## Procedure

### Step 0: Determine the closeout path

Three paths are possible, and this step picks one before any other work. The dispatch table:

|                       | Has merged PR    | No merged PR             |
|-----------------------|------------------|--------------------------|
| **Has Assignment ID**    | PR path (Step 1) | no-PR path (Step 1c)     |
| **No Assignment ID**     | ad-hoc (Step 1b) | nothing to close; stop   |

##### 0a. Try to find the Assignment's PR

The goal is to determine whether a PR exists **for the Assignment being closed out**, not whether the current branch happens to have one. `/onward` can be invoked from any worktree; the branch is incidental. Conflating "PR on this branch" with "PR for this Assignment" produces two failure modes: an unrelated open PR on the branch stops a legitimate no-PR closeout, and an unrelated merged PR on the branch routes the skill to the wrong PR.

Do not assume merge status from conversation context or the user's invocation; check GitHub directly.

**If an Assignment ID is known** (from `$ARGUMENTS` or the conversation context), look up the PR by Assignment ID; the Assignment is the identity, the branch is not:

```bash
gh pr list --state all --search "<ASSIGNMENT> in:title" --json number,title,state,mergedAt,url
```

- One **merged** PR → that is the Assignment's PR; continue to 0b (PR path).
- One **open** PR → the Assignment's PR exists but has not been merged. Report status and stop; `/onward` requires a merged PR.
- **No result** → the Assignment may have been delivered without a PR. Continue to 0b (no-PR path).
- Multiple results → rare; inspect titles, pick the one matching the Assignment's scope, or ask the operator.

**If no Assignment ID is known** (ad-hoc closeout with no prior Assignment), the PR is most likely on the current branch or was named in the invocation:

```bash
# If a PR number or URL was passed in $ARGUMENTS or mentioned in the conversation
gh pr view <number-or-url> --json state,mergedAt,number,title

# Otherwise, the current branch (the likely location of ad-hoc work)
gh pr view --json state,mergedAt,number,title

# Final fallback: recent merged PRs, pick the one matching the work under discussion
gh pr list --state merged --limit 10 --json number,title,mergedAt,headRefName,author
```

- Merged PR resolved → continue to 0b (ad-hoc path).
- Open PR resolved (and it's the PR the caller wants to close out) → report status and stop.
- Nothing found → 0b dispatches to "nothing to close out".

If the ladder returns ambiguity, ask the operator rather than guessing. Only after every step comes up empty may you conclude "no PR exists"; a PR lookup that merely didn't find the PR on the first try is not the same thing as an Assignment that was completed without a PR.

##### 0b. Dispatch

- **Merged PR found**:
  - Assignment ID is known → PR path. Continue to **Step 1**.
  - No Assignment ID → ad-hoc. Continue to **Step 1b**.
- **No merged PR exists** (after fully exhausting the ladder above):
  - Assignment ID is known → no-PR path. Continue to **Step 1c**.
  - No Assignment ID → nothing to close out. Stop and report to the operator; the agent should not invent an Assignment to document ad-hoc work that produced no artifact.

### Step 1: Gather Context (PR path)

1. Fetch the Assignment description from the tracker using the Assignment ID from `$ARGUMENTS` or the conversation context.
2. Read the merged PR (diff, description, review comments).
3. Review the conversation history for key decisions, plan deviations, and domain learnings.

Continue to Step 2.

### Step 1b: Create a Retroactive Assignment (ad-hoc path)

Work sometimes ships without a tracker Assignment: ad hoc fixes, requests that didn't warrant upfront planning, work that grew from a quick question into a PR. The closeout still needs a home in the tracker so the institutional record is complete.

1. Read the merged PR (diff, description, review comments).
2. Review the conversation history for what was done and why.
3. Create the Assignment with a summary and description derived from the actual work, not boilerplate. The description should note that this is a retroactive Assignment and briefly explain what prompted the work. `vv assignment-create` writes into the Component whose main clone contains cwd; Type, Route, and Workflow are required project fields, so the call must set all three (Type defaults to `Premise` and Workflow defaults to `Submitted`).
   ```bash
   new_id=$(vv assignment-create \
     --summary "..." \
     --description "..." \
     --route check-in)
   ```

Continue to Step 2 with the newly created Assignment ID.

### Step 1c: Gather Context (no-PR path)

Some Assignments resolve entirely outside git: tracker-admin changes, third-party config, infra-only work whose artifacts live in another system's state rather than in a diff. The Assignment still needs a closeout; there is just no PR to read.

1. Fetch the Assignment description from the tracker using the Assignment ID from `$ARGUMENTS` or the conversation context.
2. Review the conversation history for what was done: which API calls ran, what responses came back, what decisions were made, what deviated from the Assignment as written.
3. Gather whatever API-response evidence the agent captured (command outputs, response bodies, state changes observed in the target system). This is the substitute for the PR diff: thin, but it is what actually happened.

The synopsis in Step 2 must ground in these three sources. Do **not** write a pre-PR narrative that invents a code change that did not exist, and do not paper over the no-PR-ness by paraphrasing the Assignment description back as if it were an implementation report.

Continue to Step 2.

### Step 2: Write the Synopsis

Draft a comment for the Assignment. The comment MUST begin with the header `## Closeout Synopsis`; this allows a future agent to identify it programmatically among other discussion comments.

The synopsis answers three questions:

**What was built vs. what was framed?**
- Did the implementation track the Assignment's framing? Where it diverged, why?
- Was anything added, dropped, or descoped? Why?
- Were there significant departures from the prep's working plan? What drove them?

**What did we learn in the course of the work?**
- Did the implementation reveal anything the Assignment didn't anticipate?
- Any surprises about the existing code, the tooling, or the adjacent skills?

**What should downstream Assignments know?**
- Decisions that constrain or enable future work.
- Patterns established that subsequent Assignments should follow (or avoid).
- Anything a future agent would waste time rediscovering without this note.

Keep the comment concise; a future agent skimming the history should be able to read it in under a minute. Use bullet points. No preamble or pleasantries.

### Step 3: Brief Output

Report to the operator:
- Assignment ID and final state
- One-line summary of the synopsis posted
- Any downstream concerns flagged in the comment
- Note that fanout (Step 5) will also post per-spawn reports to chat, but this Step 3 report is the authoritative end-of-Bob summary

This is the agent's last opportunity to own the close narrative. Subsequent spawn reports arrive one per peer; they are the new Bobs announcing themselves, not this one. Print the report, then proceed.

### Step 4: Bookkeep and identify unblocked peers

Hand off the tracker side of the close, and collect the ids of peers this close just freed up:

```bash
vv resolve delivered <ASSIGNMENT> --reason "$SYNOPSIS" || { echo "resolve failed; aborting /onward before fanout" >&2; exit 1; }
peers=$(vv unblocked <ASSIGNMENT>)
awaiting=$(vv unblocked-sign-off <ASSIGNMENT>)
printf '%s\n' "$peers"      # surface the captured spawn list to chat for recovery
printf '%s\n' "$awaiting"   # surface the awaiting-sign-off list to chat
```

`vv resolve delivered` posts the `## Closeout Synopsis` comment and transitions State to `Delivered`; `vv unblocked` then prints the newly-pickable peer ids to stdout (one id per line, sorted, with no other chatter) and refuses only if the Assignment is somehow not resolved, which `vv resolve delivered` just guaranteed. The `|| exit 1` on the resolve is decisive: a failed bookkeeping must abort the close loudly, not fall through to a fanout that would then look empty. `$peers` carries the list into Step 5's loop; the `printf` ensures the same list reaches chat as a visible audit trail, since the recovery guidance later (in Tips) keys off "the printed ids." Neither command launches teardown; sequencing is this skill's job.

`vv unblocked-sign-off` captures the close's other freed peers: Commands and Manuals whose dependencies are now resolved but which the operator has not signed off. These are held out of the pool, so `vv unblocked` does not list them and the spawn loop never sees them; `$awaiting` carries them to Step 5's report for the operator's decision, not into the loop. Once signed off, such a peer is pickable like any other and `vv unblocked` lists it. The two queries are disjoint by construction (`$peers` is the pool, `$awaiting` is what waits on sign-off), so each freed peer reaches the loop at most once.

### Step 5: Spawn a Bob per unblocked peer

For each `<peer>` id printed in Step 4, run `vv spawn` once per id, in a bash loop:

```bash
for peer in $peers; do
  vv spawn "$peer" || continue
done
```

`vv spawn` is the canonical composed spawn: it preflights the peer, resets the managed clones, forks the peer Component's Foundation, pre-seeds the worktree's folder-trust, and runs `workmux add --background` in the peer's own target repo with the Bob's full agent command (auto-mode permissions, the scaffold env trio, Remote Control). Running it per peer is what makes the fanout cross-Component: each peer spawns into the repo its prefix names, not `/onward`'s repo.

The `|| continue` is the fanout's fault tolerance, and it is essential under two `/onward` closes running concurrently on the same newly-unblocked peer. `vv spawn`'s internal preflight refuses a peer another close already claimed (Workflow `Claimed`, or State resolved), exiting non-zero so `continue` skips it and the loop proceeds. If both closes race past preflight before either Bob has claimed, `vv spawn`'s `workmux add` refuses the second on the canonical `<prefix>-<n>` worktree-name collision, also non-zero, also skipped. Either guard catches the race with no coordination, and stderr from each `vv spawn` surfaces directly to chat.

Post a one-line report per successfully-spawned peer (Assignment id and the `wm open <prefix>-N` command, where the worktree is `vv spawn`'s canonical `<lowercase-prefix>-<number>`, e.g. `pm-40`, no `bob-` prefix). If the unblocked list is empty, this step is a no-op.

Then, for each id in `$awaiting`, post a one-line report that the peer is dependency-unblocked but **not** spawned: a Command or Manual awaiting the operator's sign-off before it can enter the pool. Do not `vv spawn` it; the fanout acts only on `$peers`. If `$awaiting` is empty, this is a no-op.

### Step 6: Teardown

Run the bare detached teardown:

```bash
vv teardown
```

This archives the worktree and kills the pane. `vv teardown` writes nothing to the tracker; the transition already happened in Step 4's `vv resolve delivered`, so there is nothing left to record.

## Tips

- **Saturation is the default, not a side effect.** If the fanout is empty, the Assignment genuinely had no downstream peers waiting on it; that is fine. If the fanout is non-empty, those peers were already waiting; `/onward` is not creating work, it is surfacing work that was held behind this close.

- **Concurrent closes are safe by construction.** Two `/onward` closes that both see the same newly-unblocked peer will both try to spawn on it. `vv spawn`'s internal preflight refuses claimed/resolved Assignments (Workflow `Claimed` or State `isResolved: true`), and its `workmux add` refuses a canonical-worktree-name collision. Either guard catches the race; you don't need to coordinate.

- **Recovery from mid-flight interruption is manual.** `/onward` is not resumable. If Step 4 succeeded (Assignment is `Delivered`) but Step 5 was interrupted mid-loop, finish the spawns by hand from the printed ids (re-running `vv spawn` per remaining peer, or invoking `/spawn` once per peer) then run `/closeout none` to tear down. Do not re-run `/onward` on the same Assignment; re-running `vv resolve delivered` would duplicate the synopsis comment.

- **Use `/closeout delivered` when you want to opt out.** A retroactive close (Step 1b) whose downstream peers were authored without this close in mind, or any close where the Bob wants to hand-pick what spawns, should use `/closeout delivered` directly.
