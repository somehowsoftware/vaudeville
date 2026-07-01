---
name: _continue_parlay
description: >
  Machinery, not a human command: the continuation `/parlay` checkpoints into.
  Converge every open PR an assignment produced, addressing each Codex comment,
  merge conflict, and CI failure as a symptom of a deeper issue, not a line-edit.
  Each round senses the PR through one deterministic command, digests a CI failure
  in a discarded context so its log never reaches this one, and judges from what
  comes back; escalates any PR that needs three rounds of patching in a single run.
---

# Continue parlay

## You arrive grounded

This skill is invoked by the Resume Brief: the first turn of this cleared session, already in the conversation above. It carries the operator's verbatim turns (the Digest) and your own Carryover, which holds the loop's starting point: which PR or PRs are open for this assignment, and anything learned in implementation a reviewer's comment will turn on. You read both on the way here, and there is nothing to fetch; the PRs themselves you resolve below. Honor the Brief's discipline throughout the loop: the latest operator turn is the live one, and any doctrine or domain term you lean on gets re-read from its source, because a cleared context presents as fluency, not as ignorance. If no Resume Brief sits above you, something invoked this skill out of band; stop and say so rather than improvise grounding.

## Converge the PRs

Automate the PR babysitting loop so the operator doesn't have to watch it. Drive three convergence targets at once: Codex comments, merge conflicts against `main`, and CI status.

An assignment routinely produces more than one PR: a substantive change in one repository plus the mechanical change a contract forces in a peer repository, each its own PR on its own branch. This loop converges **every open PR the assignment produced**, not only the one on the current branch, so the operator says it once and has all of them babysat. The common case is still a single PR, and nothing about it changes: the set is simply that one PR.

Converge the PRs one at a time, running the watch loop below against each in turn, and the run exits only once every PR has converged. Sequence rather than interleave them on purpose: the symptom-density stop reads a single PR's patch history, and folding rounds from several PRs into one ledger would blur the very signal it exists to catch. Each PR keeps its own ledger on disk and its own escalation; an escalation fires for that PR alone and hands back to the operator with the status of the whole set, so the rest are never dropped in silence.

**This loop does not merge any PR.** The merge is the operator's call after they review. Only bot-authored PRs auto-merge, where the tenant has configured that; nothing the loop does merges code to `main`. The point of the loop is to spare the operator's attention on defective code by converging on Codex before the PR reaches their review queue.

**When to use:** after a PR is open that Codex will review. A procedure reaches here through `_tender`, which invokes `/parlay` automatically at the end of its CI-green gate with the single PR it just opened, so the default path is automatic; direct invocation of `/parlay` (naming several PRs) is how an assignment's coordinated PRs get babysat together, and also how a stalled parlay is resumed after manual intervention or a bypassed auto-handoff. Run each PR's git-level steps in that PR's branch worktree.

## The shape of a round, and why it is shaped this way

The loop runs long, and its old failure was not in any one decision but in what each round left behind: every pass appended a CI log, a comment thread, and a subagent's report to a context that was never shed and was re-read in full on every later turn. The bill was that accumulation, not the work. So the round is cut to keep this context small, and the cut is worth understanding because it tells you where each piece of the work belongs.

- **`vv parlay-watch` senses; it does not decide.** It waits for Codex, then reads the PR's facts and reports only what you need to act: the convergence verdict, how many comments are open and how many arrived this pass, CI status with a handle to its log, mergeability, the reviewer's disposition on the head, and the running counts. It writes the open comments verbatim to a file — every inline finding, and any finding Codex left in a review body rather than an inline comment — and reports the counts, never the bodies, so a comment's text crosses into this context only when you read that file to triage it. The raw CI log it does not fetch at all.
- **The bookkeeping runs from your primary worktree.** `vv parlay-watch` and `vv parlay-record` sense the PR remotely (through `--repo`) and keep the ledger under this worktree's `.scratch`; they need no checkout. Run them from the worktree `/parlay` was invoked in, so the ledger has one stable home across the run. Only a PR's git-level steps (resolving a conflict, pushing a fix) need that PR's branch worktree; reaching into a peer repository's checkout to commit there does not move where the bookkeeping lives.
- **The digest crushes the CI log in a context that is then discarded.** A failed run's log is the largest thing the loop ever touches, and it must never enter this context. A subagent fetches it through the handle, crushes it to a root cause, and returns a few lines; its own context, log and all, is thrown away. It is an anti-corruption layer, not a compressor: it keeps the handle so you can fetch the raw log if its crush is thin, and it may *tag* a suspected flake but never *decides* one.
- **You judge, from what comes back.** The symptom-vs-line-edit call, the real-vs-invented-case call, the flake-vs-real-failure decision: these are yours and stay here, with the authority to act on them. The machinery hands you small, faithful inputs; it never makes the call.
- **The ledger lives on disk, not in the prose.** `vv parlay-watch` and `vv parlay-record` keep the round count, the pass count, and the open comments in a file, read fresh each round. That is why the escalation backstop works now where it did not before: the round count is no longer lost in accumulated context, and it is no longer yours to set — `vv parlay-watch` advances it by reading the PR head, so a code-changing round is a fact about a landed commit, not a disposition you record.

## Inputs

- `prs` (required): one or more PR numbers or URLs. Default: the single PR on the current branch. The automatic `_tender → /parlay` hand-off passes exactly one; the operator names several, or the Carryover carries them, when an assignment produced coordinated PRs.
- `interval` (optional): the upper bound, in seconds, on a single `vv parlay-watch` call's wait for Codex, passed through as `--interval`. Default **270**; the wait exits early the moment Codex rules on the head (a `+1` or a review) and the loop re-senses across calls until the reviewer's patience runs out. The cap sits just under the prompt cache's 5-minute TTL so a fall-through wake-up still hits warm cache; 300 would miss, and anything from 300 to ~1200 pays the cache miss without amortizing it.
- `max_iterations` (optional): the pass cap, passed through as `--max-iterations`. Default **20**. `vv parlay-watch` reports `stop: yes` once the loop reaches it; stop and hand back to the operator when it does.

## Procedure

### 1. Resolve the PRs

Take the set of PRs to converge from the Carryover, or from a direct invocation that named them. If none is named, derive the single PR from the current branch:

```bash
gh pr view --json number,url,headRefName
```

Fail fast if no PR resolves at all: there is nothing to parlay with. Then converge the set one PR at a time: run the watch loop below against each, passing its number and `--repo owner/repo` to every `vv parlay-watch` and `vv parlay-record` call (the `--repo` keys the ledger to that PR's full identity, so peer PRs that happen to share a number do not share state). Run the `vv` commands themselves from this primary worktree; reach into a PR's own branch worktree only for its git-level steps. The run exits only once every resolved PR has converged.

### 2. Watch loop

Run this loop for the PR currently being converged. Keep one rule in view from the first pass: a run of individually-legitimate fixes almost always means a design decision introduced the fragility Codex keeps poking at, not that the reviewer found that many independent defects. **This bad decision is often not visible to the agent that authored it, so do not rationalize it away.** The loop hard-stops at three code-changing rounds for exactly that reason; the cheapest move once you sense it is to run the [Repeated-symptom escalation](#repeated-symptom-escalation) early rather than keep patching.

Each pass:

1. **Sense.** Run the watch command, which waits for Codex to rule on the head (exiting early the moment it does, or once the wait runs out of patience) and then reports the round's facts. Give it a timeout above the interval so the wait can run to completion:

   ```bash
   vv parlay-watch <pr> --interval 270 --max-iterations 20   # add --repo owner/repo for a peer PR
   ```

   It prints `convergence`, `open-comments` (a count and a file path), `new-this-pass`, `ci`, `mergeability`, `reviewer` (the reviewer's disposition on the head: `findings`, `clean`, or `pending`), `rounds`/`escalate`, `passes`/`stop`, and `head`.

2. **Branch on the verdict.** The verdict is the single directive, and the escalation overrides a convergence verdict by construction — a PR that looks converged on the very pass its third code-changing round lands still escalates.
   - `convergence: merged` → the PR was merged out from under the loop (the strongest convergence there is). **This PR has converged via merge.** Record it for the Report and move to the next PR.
   - `convergence: closed` → the PR was closed without merging. The loop has nothing left to converge: stop and hand back to the operator with the PR's state, the same severity as the pass cap.
   - `convergence: escalate` → three code-changing rounds have landed. Route to [Repeated-symptom escalation](#repeated-symptom-escalation) now, before the steps below and regardless of CI, mergeability, or the reviewer. The watch reports this the moment the third round trips, even on an otherwise green and clean pass, so a converged-looking PR cannot carry the loop past the stop. It is never yours to waive, in its open form or its quiet one (judging the findings independent and pressing on); the section says why.
   - `convergence: signed-off` → Codex left a `+1` current to this head; it has seen this code and cleared it. The sign-off is an accelerator, not the only path: it lets a settled PR converge without waiting the patience window out. **This PR has converged via Codex sign-off.** Record it for the Report and move to the next PR.
   - `convergence: steady-state` → nothing open, mergeable, and green, and the reviewer has settled on this head without a fresh sign-off: Codex reviewed this commit and every comment it left is disposed of, or the wait for a review has run out of patience and its silence reads as a skip. **This PR has converged via steady state.** Record it for the Report and move to the next PR.
   - `convergence: keep-going` → there is work, or Codex has not yet ruled on the current head and the wait for its review still has patience. If `stop: yes`, the pass cap is reached without convergence: stop and hand back to the operator with the current `ci`, `mergeability`, and open-comment state, the same severity as an escalation. Otherwise do the steps below and loop back to step 1; when the only thing outstanding is Codex's review of the head, the steps are no-ops and the loop simply re-senses, waiting for it — an empty comment queue is not convergence until the reviewer has weighed in on this code or the wait for it has run out.

3. **Resolve a conflict, if any.** When `mergeability: conflicting`, resolve it before anything else (see [Resolving conflicts](#resolving-conflicts)). A clean resolution commits a merge and pushes; the next pass's sense waits out the interval and re-reads CI for the new HEAD, so there is no separate CI gate to run here. A conflict you cannot resolve with confidence escalates, the same severity as the pass cap.

4. **Digest a CI failure, if any.** When `ci: red`, spawn the [digest subagent](#the-digest-subagent) on the run handle the sense reported. It returns a crushed root cause (and may tag a suspected flake); the raw log never enters this context. Then **you decide**:
   - A real failure your change caused → fix it with the same symptom-vs-root-cause lens you apply to comments, then continue to step 6.
   - A failure you judge exogenous (a flake the digest tagged and you agree is infra, an area your diff never touched, anything you cannot confidently attribute to your change) → **stop and escalate.** Hand back to the operator with the run handle and the digest's root cause. Do not retry, do not paper over. The test is: can you name the file or module your change touched that the failing check exercises? If you are guessing, it is exogenous.

5. **Triage the open comments, if any.** When `open-comments` is above zero, read that file directly — it holds, verbatim, every reviewer comment not yet disposed of (inline findings and any finding Codex left in a review body), re-rendered whole each pass so handling a conflict or CI failure first never loses one. For each comment, settle its disposition and the wording you will reply with; the reply is posted when you record the comment in step 6, so deciding it is part of triage:
   - **First, ask whether the case is real.** Codex sometimes flags a concern that only matters for a case Vaudeville does not have: guarding an input the intended use cannot produce, handling a configuration the design rules out. When the suggestion serves a hypothetical rather than Vaudeville as it is actually intended to be used, the disposition is a **reasoned rejection**: change no code, and the reply explains why the case does not apply. Hold the line tightly: reject the invented case, never a real defect whose fix is merely inconvenient. If you cannot name the concrete case the comment assumes and say why the intended use never reaches it, it is a real finding; treat it as one.
   - **Otherwise, treat the comment as a symptom, not a spec.** Ask what underlying problem would make a reviewer raise this, and do the more durable fix when there is one (see [Symptom vs. line-edit](#symptom-vs-line-edit)); the reply names what you changed and why the underlying problem is gone.

6. **Commit, push, and record each disposition with its reply.** If any code changed, commit and push with plain git as an appended commit, never an amend or force-push over the prior one (`_tender`'s [Revising a tendered PR](../_tender/SKILL.md#revising-a-tendered-pr) spells out why). Stage tracked edits and new files alike, since a fix that adds a regression test must not be left half-committed:

   ```bash
   git add -A
   git commit -m "<TICKET>: Address Codex review"
   git push
   ```

   Then record each comment you disposed of, one command per comment, which posts your reply to it and clears it from the open queue in a single act:

   ```bash
   vv parlay-record <pr> <comment-id> --reply "<what changed and why, or the reasoning for changing no code>"   # add --repo for a peer PR
   ```

   Recording and replying are one command on purpose. The reply used to be a separate manual `gh` post beside the `vv parlay-record` that recorded the disposition, and an unenforced manual step is the one that gets dropped — the dropped-reply regression this fold closes. So there is no recording without replying: the post runs first, and only a posted reply clears the comment. The reply threads under an inline comment, or lands as a new PR comment for a conversation comment or a review-body finding. Record every comment you disposed of, a fix and a reasoned rejection alike; `vv parlay-record` reports what is now addressed and what is still open. It does not touch the escalation count, and no flag does: a round counts toward the three-round stop only when it landed a commit, which the next sense reads off the moved PR head. A round of only reasoned rejections pushes nothing, so its head holds and it never counts — automatically, with nothing for you to assert. The next sense reports `convergence: escalate` once that landed commit is the third; heeding it is step 2, not a step of its own.

### 3. Report

On exit, surface one entry per PR in the set, and, when the set held more than one, a one-line roll-up of how many converged. For each PR:
- The convergence path the loop actually fired on: **merge** (`convergence: merged`), **Codex sign-off** (`convergence: signed-off`), or **steady-state convergence** (`convergence: steady-state`). Report the path the loop took, not the one that comes to mind, and never assert a sign-off the verdict did not report. A PR that Codex never reviews (it occasionally skips one, more often a doc-only change) converges via steady state once the wait for a review times out.
- Rounds and passes run (from the last sense's report).
- Number of Codex comments addressed, and any you disagreed with and replied to without changing code.
- Merge-main commits made (if any) and whether the PR is now mergeable.
- Final CI status: green, or red with the reason for escalation.
- The PR URL.

## The digest subagent

When CI is red, spawn a subagent (the Task tool) whose context is discarded after it returns, so the raw log it reads never enters this one. Give it the run handle and repository the sense reported, and this prompt:

> You are a digest subagent for a PR convergence loop. Your context is thrown away after you return; only your final message crosses back, so it must be small and it must *be* the digest, not a report about your work.
>
> CI run `<handle>` for `<owner/repo>` has failed. Do this and nothing else:
>
> 1. Fetch the failed log: `gh run view <handle> --repo <owner/repo> --log-failed`.
> 2. Crush it to the root cause: name the failing job, step, or test, and quote the few lines that show the actual error — the assertion, the last frame of the traceback, the type error. Cut everything else: setup output, passing steps, timestamps, noise.
> 3. Keep the handle: end with `raw log: run <handle>` so the judge can fetch the full log if your crush is thin. You are an anti-corruption layer, not a destroyer of evidence — if the failure is ambiguous or has no single root cause, say so and keep more of the log rather than guess.
> 4. You **may** tag the failure `SUSPECTED FLAKE: <why>` if it looks like infrastructure (a network blip, a runner error, a timeout unrelated to the diff). You **must not** decide it; the judge decides.
>
> Return only the crushed root cause, the handle, and the optional flake tag — a few lines. Do not fix, reply, or push anything: you sense and crush; the judge decides and acts.

You read the few lines it returns and decide, in step 4 of the loop. If its crush is too thin to decide on, fetch the raw log yourself through the handle — that is what the handle is for — but do so knowing the log lands in this context, so reach for it only when the crush genuinely will not serve.

## Resolving conflicts

When the sense reports `mergeability: conflicting`:

```bash
git fetch origin main
git merge origin/main
```

**Resolve by merging, never by rebasing.** Rebasing onto `main` rewrites already-pushed history, which [Revising a tendered PR](../_tender/SKILL.md#revising-a-tendered-pr) reserves for the harm-is-the-history case, not for recording a conflict resolution. Merge creates a merge commit, keeps history append-only, and pushes without a force.

If the merge is clean, git has already created the merge commit; push it. If there are conflicts, resolve them with the same symptom-vs-line-edit scrutiny you apply to comments, carrying two questions through every conflict:

1. **Is this a textual merge, or did `main` invalidate the premise of this PR?** If a refactor on `main` changes the shape of code this PR depends on, the resolution may not be merging two diffs; it may be re-implementing the PR's change on top of the new shape. Don't paper over.
2. **Would the merged result silently revert either side's intent?** If yes, stop; the right call is probably not a merge-time fix.

If you can resolve with confidence, `git add` the resolved files, commit, and push; the next sense re-reads CI for the merge commit. If you cannot (the diff touches code whose intent is unclear, the resolution would silently revert either side, or `main` has invalidated the PR's premise), abort and escalate:

```bash
git merge --abort
```

Treat this with the same severity as the pass cap: stop the loop, hand back to the operator with the conflicted files and what made the resolution unclear. A clean merge-main resolution lands a commit, so the next sense reads the moved head and counts it as a code-changing round; there is no `vv parlay-record` for it, since it disposes of no comment, and the moved head is the whole signal. Counting it is deliberate: a run that needs three merge resolutions in one pass earns the operator's eyes as much as three rounds of Codex fixes, and over-counting is the safe error — it surfaces a run for a look where under-counting would let a real escalation slip.

## Symptom vs. line-edit

This is the part that matters. Codex review comments are usually correct about *what* they noticed (a redundant check, a naming inconsistency, a missing edge case) but the fix they imply is often the smallest possible patch. The right fix is frequently one level deeper: the code shape that produced the symptom.

Concrete heuristics:

- **Repeated symptoms in different files** → the abstraction is wrong, not the individual callsites.
- **A null-check Codex wants** → more often, a type or invariant that guarantees non-null upstream.
- **"Consider renaming X"** → if the name is wrong, other call sites are probably confused too; rename everywhere and update docs.
- **"Add a comment explaining Y"** → usually the code needs to be rewritten so the behavior is self-evident.

If the symptom-level fix is genuinely the right call (a true off-by-one, a typo, a factual error in docs), do it and move on. The heuristic is: "before I apply the exact change Codex suggests, can I describe a code shape where this comment would never have been written?" That question hunts for a *better fix*; it must not become a licence to *invent* one. Sometimes the only code shape in which the comment would never have been written is one where Vaudeville handles a case it does not actually have; then the comment is guarding a hypothetical, and the disposition is the reasoned rejection from step 5, not a build of any size.

## Repeated-symptom escalation

Three code-changing rounds in one run is a hard stop: the run does not go forward from here until the operator answers. It is not a message you post and then keep working past, and it is not the agent's to waive — the loop halts at the trip and stays halted until the operator says keep going, redesign, or close. Your own renewed conviction does not lift it; only the operator's word does.

The reason the stop is the operator's and not yours is the one thing this situation reliably hides. Codex catches symptom-level errors well and conceptual misframings poorly, so a run of correct-looking patches is the signal that what you are patching sits downstream of a frame the reviewer could not see — a frame you authored and still cannot see, or there would not be three rounds of it. At the trip you cannot tell your own fluency from the truth, and that is exactly why the call the trip turns on — were these findings independent, or symptoms of one misframing — is not yours to make. The better your case for "independent, keep going," the more precisely you are standing where the stop exists to catch you: that case is what the situation manufactures. The moment you find yourself composing the reason you need not surface, the composing is the signal that you must.

So do not read this rule for its spirit, and do not litigate whether this "really" amounts to three rounds — to interpret the stop is to exercise the very judgment it withdraws. Where it is unclear, it counts, and you stop.

At the trip, halt the loop and produce the following — for the operator to decide on, never to clear yourself — then surface all of it and wait:

1. **Run a Five Whys on the symptom density.** Before you write any synthesis, and before anything reaches the operator, interrogate the symptom density itself: ask why this run needed three rounds of correct-looking fixes, take that answer and ask why of *it*, and repeat (each answer becoming the next question) until the chain bottoms out in a root cause that is mechanical, a property of the code or the design, rather than narrative. A single question answered once is not a Five Whys: "what frame would have made these comments unnecessary?" is answered fluently by the very agent whose framing produced the defects, and a self-flattering answer that recasts the symptoms as a single benign frame passes for a root cause without being one. The iterative why-of-the-why is the forcing function that blocks that one-shot rationalization. **This interrogation is mandatory; it is not yours to skip or to waive, nor to collapse into a single confident answer**, the same standing as the trip that routed you here. Run it first, because a synthesis written before it becomes the conclusion the whys are then bent to justify. Expect the root cause to be uncomfortable: a genuine one routinely exposes a defect already pushed that the reviewer never caught, which is the whole reason three rounds tripped the stop.

2. **Synthesize across the run, from the root cause.** Re-read every Codex comment from this parlay's iterations and write the synthesis *from* the root cause the Five Whys reached: name what the comments are symptoms of, grounded in that root cause rather than in a fresh open question. The synthesis carries the root cause forward, so the operator sees the interrogation's result and not merely its conclusion.

3. **Recommend a course, and hand back.** Weigh in with one course and argue for it from the root cause the Five Whys reached; the Bob's read of what to do next is the most valuable input the operator has here. The menu is illustrative and incomplete:
   - Implement the same concept more carefully on a fresh branch.
   - Redesign the mechanism but retain the overall solution.
   - Revisit the assignment; its framing may be the source of the misdirection.
   - File a dependent Premise and return the current one.
   - Close the PR and reattempt — the same Bob, carrying forward what didn't work, is usually best-positioned to author the next attempt.
   - Something the menu doesn't cover.

   Surface the synthesis, the recommendation, the menu, and the PR's current state, then wait. The corrective action is the operator's to choose and the two of you to resolve together; the loop does not script it, does not close the PR on its own, and does not resume on anything but the operator's explicit answer.

   When that answer is keep going, enact it with `vv parlay-waive <pr>` (add `--repo owner/repo` for a peer PR). The waiver is the operator's; the command only carries out their explicit word, never your own renewed conviction. It lifts the escalation while leaving the round count standing, so the next sense reports the real convergence verdict again and the loop resumes at step 1 — and a third code-changing round past the waiver escalates afresh, a louder alarm rather than a clean slate. The other courses exit this loop instead of resuming it: a redesign, a close, or a returned assignment takes no waiver.

## On failure

- **Conflict cannot be resolved with confidence** → `git merge --abort`, stop, hand back to the operator with the list of conflicted files.
- **CI red from a failure you judge exogenous** → stop, hand back to the operator with the run handle and the digest's root cause.
- **Pass cap reached (`stop: yes`)** → stop and hand back to the operator with a summary of outstanding comments, merge state, and CI state.
- **Commit or push fails** → do not retry blindly. Investigate, fix, then resume.
