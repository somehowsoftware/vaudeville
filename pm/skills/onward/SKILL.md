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

Draft the synopsis body for the Assignment. Do not write the `## Closeout Synopsis` header yourself: Step 4's `vv resolve delivered` prepends it, and that is what lets a future agent identify the comment programmatically among other discussion comments.

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

Three commands, each run on its own:

```bash
vv resolve delivered <ASSIGNMENT> --reason "$(cat <<'SYNOPSIS'
- Tracked the framing; dropped the `--strict` flag as unreachable.
- `$HOME`-relative paths broke under the test runner; switched to absolute.
- Downstream: PM-88 should reuse the fixture in `tests/conftest.py`.
SYNOPSIS
)"
```

```bash
vv unblocked <ASSIGNMENT>
```

```bash
vv unblocked-sign-off <ASSIGNMENT>
```

The body is the synopsis you drafted in Step 2, typed in verbatim: a paraphrase written now is the version that lands, and Step 6 ends the only session that could tell the difference. It starts at your first line — `vv resolve` prepends the `## Closeout Synopsis` header itself.

The quote marks in `<<'SYNOPSIS'` are the mechanism, not decoration. Under a bare `<<SYNOPSIS` the shell treats the body as a double-quoted string: your backticked command names run as commands and your `$` names expand to nothing, and that wreckage is what lands — on an Assignment now `Delivered` that nobody reads again.

If `vv resolve delivered` fails, stop: do not run `vv unblocked`, do not spawn, do not tear down. Report it and leave the worktree standing. Failing quietly here is indistinguishable from succeeding — `vv unblocked` refuses an unresolved Assignment and prints no ids, which reads exactly like a close that freed nobody, and Step 6 would then destroy the evidence.

`vv unblocked` prints the newly-pickable peer ids, one per line, sorted. `vv unblocked-sign-off` prints the close's other freed peers: Commands and Manuals whose dependencies are now resolved but which the operator has not signed off, so they are held out of the pool. Sign-off is exactly what separates the two lists, so no peer appears in both. The first is what Step 5 spawns; the second is only reported.

### Step 5: Spawn a Bob per unblocked peer

Issue one `vv spawn` command per id that `vv unblocked` printed, each as its own separate call, reading the ids off Step 4's output.

Separately, because each spawn is an irreversible act with its own outcome and this is the only pass anyone makes over it. Step 6 ends this session; the record of these calls is the record. Batch fifteen ids into one command and they share one exit status and one stream of stderr, so the peer that failed to spawn cannot be told from the fourteen that worked — and the graph reads closed while that successor never starts.

Do not delegate the repetition to the shell. `/onward` runs under whatever shell the harness inherited from the host login shell, and Vaudeville does not specify one. On macOS it is zsh, which does not word-split an unquoted parameter expansion: a loop over a captured, newline-joined id list runs exactly once and hands `vv spawn` the whole blob as a single argument, which it rejects as a malformed id. Shell state does not survive between your Bash calls either, on any shell, so a list captured in one call is unset in the next.

```bash
vv spawn BACKUP-9
```

```bash
vv spawn BACKUP-10
```

`vv spawn` resolves each peer into the repo its prefix names, so a cross-Component fanout needs nothing extra from you; stay in this worktree.

Every printed id leaves this step in one of two states: it has a Bob, or it is named in your chat report as unspawned with what went wrong. A failed spawn does not stop the fanout — go on to the next id — but the exit status alone will not tell you which state you are in: a peer another close already claimed and a peer whose fork broke both exit non-zero, and only one of them has a Bob. Read what the command said.

Post a one-line report per spawned peer: the Assignment id and the `wm open <prefix>-N` command, where the worktree is `vv spawn`'s canonical `<lowercase-prefix>-<number>` (e.g. `pm-40`, no `bob-` prefix).

Then, for each id from `vv unblocked-sign-off`, post a one-line report that the peer is dependency-unblocked but **not** spawned: a Command or Manual awaiting the operator's sign-off before it can enter the pool. Do not spawn it.

If either list was empty, its part of this step is a no-op.

### Step 6: Teardown

Run the bare detached teardown:

```bash
vv teardown
```

This archives the worktree and kills the pane. `vv teardown` writes nothing to the tracker; the transition already happened in Step 4's `vv resolve delivered`, so there is nothing left to record.

## Tips

- **Saturation is the default, not a side effect.** If the fanout is empty, the Assignment genuinely had no downstream peers waiting on it; that is fine. If the fanout is non-empty, those peers were already waiting; `/onward` is not creating work, it is surfacing work that was held behind this close.

- **Concurrent closes are safe by construction.** Two `/onward` closes that both see the same newly-unblocked peer will both try to spawn on it. `vv spawn`'s internal preflight refuses claimed/resolved Assignments (Workflow `Claimed` or State `isResolved: true`), and its `workmux add` refuses a canonical-worktree-name collision. Either guard catches the race; you don't need to coordinate.

- **Recovery from mid-flight interruption is manual.** `/onward` is not resumable. If Step 4 succeeded (Assignment is `Delivered`) but Step 5 was interrupted partway, finish the spawns from the ids `vv unblocked` printed (re-running `vv spawn` per remaining peer, or invoking `/spawn` once per peer) then run `/closeout none` to tear down. Do not re-run `/onward` on the same Assignment; re-running `vv resolve delivered` would duplicate the synopsis comment.

- **Use `/closeout delivered` when you want to opt out.** A retroactive close (Step 1b) whose downstream peers were authored without this close in mind, or any close where the Bob wants to hand-pick what spawns, should use `/closeout delivered` directly.
