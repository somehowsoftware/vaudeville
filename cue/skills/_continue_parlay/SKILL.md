---
name: _continue_parlay
description: >
  Machinery, not a human command: the continuation `/parlay` checkpoints into.
  Converge every open PR an assignment produced, addressing each Codex comment,
  merge conflict, and CI failure as a symptom of a deeper issue, not a line-edit.
  Each round senses the PR through one deterministic command, digests a CI failure
  in a discarded context so its log never reaches this one, and judges from what
  comes back; escalates any PR that needs three forced rounds — reviewer fixes or
  merge resolutions — in a single run.
---

# Continue parlay

## You arrive grounded

This skill is invoked by the Resume Brief: the first turn of this cleared session, already in the conversation above. It carries the operator's verbatim turns (the Digest) and your own Carryover, which holds the loop's starting point: which PR or PRs are open for this assignment, and anything learned in implementation a reviewer's comment will turn on. You read both on the way here, and there is nothing to fetch; the PRs themselves you resolve below. Honor the Brief's discipline throughout the loop: the latest operator turn is the live one, and any doctrine or domain term you lean on gets re-read from its source, because a cleared context presents as fluency, not as ignorance. If no Resume Brief sits above you, something invoked this skill out of band; stop and say so rather than improvise grounding.

## Converge the PRs

Automate the PR babysitting loop so the operator doesn't have to watch it. Drive three convergence targets at once: Codex comments, merge conflicts against `main`, and CI status.

An assignment routinely produces more than one PR: a substantive change in one repository plus the mechanical change a contract forces in a peer repository, each its own PR on its own branch. This loop converges **every open PR the assignment produced**, not only the one on the current branch, so the operator says it once and has all of them babysat. The common case is still a single PR, and nothing about it changes: the set is simply that one PR.

Converge the PRs one at a time, running the watch loop below against each in turn, and the run exits only once every PR has converged. Sequence rather than interleave them on purpose: the symptom-density stop reads a single PR's patch history, and folding rounds from several PRs into one ledger would blur the very signal it exists to catch. Each PR keeps its own ledger on disk and its own escalation; an escalation fires for that PR alone and carries the status of the whole set with it, so the rest are never dropped in silence.

**This loop does not merge any PR.** The merge is the operator's call after they review. Only bot-authored PRs auto-merge, where the tenant has configured that; nothing the loop does merges code to `main`. The point of the loop is to spare the operator's attention on defective code by converging on Codex before the PR reaches their review queue.

**When to use:** after a PR is open that Codex will review. A procedure reaches here through `_tender`, which invokes `/parlay` automatically at the end of its CI-green gate with the single PR it just opened, so the default path is automatic; direct invocation of `/parlay` (naming several PRs) is how an assignment's coordinated PRs get babysat together, and also how a stalled parlay is resumed after manual intervention or a bypassed auto-handoff. Run each PR's git-level steps in that PR's branch worktree.

## The shape of a round, and why it is shaped this way

The loop runs long, and its old failure was not in any one decision but in what each round left behind: every pass appended a CI log, a comment thread, and a subagent's report to a context that was never shed and was re-read in full on every later turn. The bill was that accumulation, not the work. So the round is cut to keep this context small, and the cut is worth understanding because it tells you where each piece of the work belongs.

- **`vv parlay-watch` senses; it does not decide.** It waits for Codex, then reads the PR's facts and reports only what you need to act: the convergence verdict, how many comments are open and how many arrived this pass, CI status with a handle to its log, mergeability, the reviewer's disposition on the head, and the running counts. It writes the open comments verbatim to a file — every inline finding, and any finding Codex left in a review body rather than an inline comment — and reports the counts, never the bodies, so a comment's text crosses into this context only when you read that file to triage it. The raw CI log it does not fetch at all.
- **The bookkeeping runs from your primary worktree.** `vv parlay-watch` and `vv parlay-record` sense the PR remotely (through `--repo`) and keep the ledger under this worktree's `.scratch`; they need no checkout. Run them from the worktree `/parlay` was invoked in, so the ledger has one stable home across the run. Only a PR's git-level steps (resolving a conflict, pushing a fix) need that PR's branch worktree; reaching into a peer repository's checkout to commit there does not move where the bookkeeping lives.
- **The digest crushes the CI log in a context that is then discarded.** A failed run's log is the largest thing the loop ever touches, and it must never enter this context. A subagent fetches it through the handle, crushes it to a root cause, and returns a few lines; its own context, log and all, is thrown away. It is an anti-corruption layer, not a compressor: it keeps the handle so you can fetch the raw log if its crush is thin, and it may *tag* a suspected flake but never *decides* one.
- **You judge, from what comes back.** The symptom-vs-line-edit call, the real-vs-invented-case call, the flake-vs-real-failure decision: these are yours and stay here, with the authority to act on them. The machinery hands you small, faithful inputs; it never makes the call.
- **The ledger lives on disk, not in the prose.** `vv parlay-watch` and `vv parlay-record` keep the round count, the pass count, and the open comments in a file, read fresh each round. That is why the escalation backstop works now where it did not before: the round count is no longer lost in accumulated context, and it is no longer yours to set — `vv parlay-watch` folds it from the PR head's provenance, counting a forced round (a reviewer fix, or a merge that reconciled the base) and passing over the progress you simply authored.

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

Run this loop for the PR currently being converged. Keep one rule in view from the first pass: a run of individually-legitimate fixes almost always means a design decision introduced the fragility Codex keeps poking at, not that the reviewer found that many independent defects. **This bad decision is often not visible to the agent that authored it, so do not rationalize it away.** The loop hard-stops at three forced rounds for exactly that reason; the cheapest move once you sense it is to run the [Repeated-symptom escalation](#repeated-symptom-escalation) early rather than keep patching.

Each pass:

1. **Sense.** Run the watch command, which waits for Codex to rule on the head (exiting early the moment it does, or once the wait runs out of patience) and then reports the round's facts. Give it a timeout above the interval so the wait can run to completion:

   ```bash
   vv parlay-watch <pr> --interval 270 --max-iterations 20   # add --repo owner/repo for a peer PR
   ```

   It prints `convergence`, `open-comments` (a count and a file path), `comment-history` (the file path where the full run's reviewer comments are kept, verbatim, for the escalation), `new-this-pass`, `ci`, `mergeability`, `reviewer` (the reviewer's disposition on the head: `findings`, `clean`, or `pending`), `rounds`/`escalate`, `passes`/`stop`, and `head`.

2. **Branch on the verdict.** The verdict is the single directive, and the escalation overrides a convergence verdict by construction — a PR that looks converged on the very pass its third forced round lands still escalates.
   - `convergence: merged` → the PR was merged out from under the loop (the strongest convergence there is). **This PR has converged via merge.** Record it for the Report and move to the next PR.
   - `convergence: closed` → the PR was closed without merging. The loop has nothing left to converge: stop and hand back to the operator with the PR's state, the same severity as the pass cap.
   - `convergence: escalate` → three forced rounds have landed. Route to [Repeated-symptom escalation](#repeated-symptom-escalation) now, before the steps below and regardless of CI, mergeability, or the reviewer. The watch reports this the moment the third round trips, even on an otherwise green and clean pass, so a converged-looking PR cannot carry the loop past the stop. It is never yours to lift on your own conviction, open (a waiver on your own say-so) or quiet (judging the findings independent and pressing on); an independent read is what lifts it, and the section says how.
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
   FIX_SHA=$(git rev-parse HEAD)   # the commit that answered every finding you fixed this pass
   ```

   Then record each comment you disposed of, one command per comment, which posts your reply to it and clears it from the open queue in a single act:

   ```bash
   # a fix: name the commit that answered it, so the next sense counts a reviewer-forced round
   vv parlay-record <pr> <comment-id> --reply "<what changed and why the problem is gone>" --fix-sha "$FIX_SHA"   # add --repo for a peer PR
   # a reasoned rejection that changed no code: --rejected, which counts toward no forced round
   vv parlay-record <pr> <comment-id> --reply "<why the case does not apply>" --rejected
   ```

   Recording and replying are one command on purpose. The reply used to be a separate manual `gh` post beside the `vv parlay-record` that recorded the disposition, and an unenforced manual step is the one that gets dropped — the dropped-reply regression this fold closes. So there is no recording without replying: the post runs first, and only a posted reply clears the comment. The reply threads under an inline comment, or lands as a new PR comment for a conversation comment or a review-body finding. Record every comment you disposed of, a fix and a reasoned rejection alike, and mark which it was: a fix takes `--fix-sha` naming the commit that answered it — the one you just pushed — and a reasoned rejection takes `--rejected`. `vv parlay-record` reports what is now addressed and what is still open. That sha is the one thing you assert toward the count, and it still does not set it: it only names the commit, so the next sense counts a reviewer-forced round when it reads that the commit landed. A rejection names no commit and counts toward nothing. The count stays `vv parlay-watch`'s to fold from the head's provenance — a recorded fix commit, or a merge that reconciled the base — never a disposition you assert. The next sense reports `convergence: escalate` once that forced round is the third; heeding it is step 2, not a step of its own.

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

Treat this with the same severity as the pass cap: stop the loop, hand back to the operator with the conflicted files and what made the resolution unclear. A clean merge-main resolution lands a merge commit, so the next sense reads its two parents and counts a forced round; there is no `vv parlay-record` for it, since it disposes of no comment — the merge's shape is the whole signal. Counting it is deliberate: a merge is a round the base forced, and a run that needs three of them in one pass earns the operator's eyes as much as three rounds of Codex fixes.

## Symptom vs. line-edit

This is the part that matters. Codex review comments are usually correct about *what* they noticed (a redundant check, a naming inconsistency, a missing edge case) but the fix they imply is often the smallest possible patch. The right fix is frequently one level deeper: the code shape that produced the symptom.

Concrete heuristics:

- **Repeated symptoms in different files** → the abstraction is wrong, not the individual callsites.
- **A null-check Codex wants** → more often, a type or invariant that guarantees non-null upstream.
- **"Consider renaming X"** → if the name is wrong, other call sites are probably confused too; rename everywhere and update docs.
- **"Add a comment explaining Y"** → usually the code needs to be rewritten so the behavior is self-evident.

If the symptom-level fix is genuinely the right call (a true off-by-one, a typo, a factual error in docs), do it and move on. The heuristic is: "before I apply the exact change Codex suggests, can I describe a code shape where this comment would never have been written?" That question hunts for a *better fix*; it must not become a licence to *invent* one. Sometimes the only code shape in which the comment would never have been written is one where Vaudeville handles a case it does not actually have; then the comment is guarding a hypothetical, and the disposition is the reasoned rejection from step 5, not a build of any size.

## Repeated-symptom escalation

Three forced rounds in one run is a hard stop. The loop does not go forward from here on your own say-so, because the judgment the next move turns on — whether these were independent findings or symptoms of one misframing — is the judgment this moment has taken away from you.

Here is why it is taken away, and it is the one thing the situation reliably hides. Codex catches symptom-level errors well and conceptual misframings poorly, so a run of correct-looking patches is the signal that what you are patching sits downstream of a frame the reviewer could not see — a frame you authored, and still cannot see, or there would not be three rounds of it. At the trip your own sense of *this is right* reads green exactly where it is most wrong: fluency in a frame is indistinguishable, from the inside, from clarity about it. So the better your case for "independent, keep going," the more precisely you are standing where the stop exists to catch you — that case is what the situation manufactures, not evidence against it. The moment you find yourself composing the reason you need not surface this, the composing is the signal that you must.

A judge who cannot be impartial is not asked to weigh the evidence more carefully; he is recused, and another judge rules. That is your position at the trip, not a failing to try harder against. So do not work out what went wrong — that is the disqualified gauge turned on itself — and do not read this rule for its spirit or litigate whether this "really" amounts to three rounds, because to interpret the stop is to exercise the judgment it withdraws. Where it is unclear, it counts, and you stop. What you do instead is convene an independent party, give it what it needs to rule, and carry its ruling back to the operator.

1. **Convene an independent committee.** Put the halt to a `/panel` — a parallel cast of clean-context reviewers who never learned your frame — choosing the cast for the medium of the halted work according to the `/panel` skill. You alone hold the history, so you brief it; but brief it by narrating **what happened** — the goal you pursued, what got settled along the way, what you built, what Codex flagged — and not **what it means**. The reading of the root cause is the one thing you are recused from, and the moment you hand it over you have rebuilt your own broken gauge inside the committee; a second opinion is independent only while its source is not the thing being measured. Give the committee the substrate to rule on for itself: the diff, and every reviewer comment from the run — not the open queue you triage from, which empties as you dispose each round, but the full history, since the repetition across rounds is the evidence the stop rests on and a committee shown only what is still open cannot see it. `vv parlay-watch` writes that history verbatim to the `comment-history` file it reports. Its read then rests on the artifact, not on your account of it, and `/panel`'s own gate screens your brief for a frame smuggled in as fact before a reviewer sees it. One check is yours, and you are reliable at it: whether you under-briefed. If you left out something the committee needed — a constraint, a decision already made, part of the goal — add it and re-brief. That corrects what it rules on; it is not overruling what it rules.

2. **Take its read as the diagnosis — then carry it to the operator; enacting it is not yours.** Where the committee's lenses converge, that convergence is the diagnosis the stop was holding out for, and you are recused from setting it aside on the strength of the frame it distrusts. But independence from your frame is not independence from the situation. The committee ruled on the task as it was handed it, and the escalation is sometimes over something that should not have been built at all — where the faithful fix the committee names is a perpetuation of the same mistake. Seeing past the task to whether the task was worth doing is the one blind spot the committee shares with you; neither of you was convened to doubt the goal. The operator sits outside that frame, so that judgment is theirs, and it is why the stop hands back to them and not to you. Bring them the committee's read and the course you would take on it — your read of what to do next is worth offering, and usually sound once the diagnosis itself came from outside you — and wait. You are not handing the operator the details to work; you are asking them to confirm the road is worth walking before you walk it, because the escalation may be over something silly and the committee's fix a way of perpetuating it.

   The terminal courses were never yours to take. Closing the PR, returning the assignment to the pool for another Bob, abandoning it outright — each is a `/closeout` only the operator invokes, by typing the command, and the loop offers no way around that. The one course that is yours to enact resumes the loop, and only on the operator's word: `vv parlay-waive <pr>` (add `--repo owner/repo` for a peer PR), which lifts the halt for a bounded fix the operator has agreed is worth making. The waiver carries out their word, never a second wind of your own; it leaves the round count standing, so a third forced round past it escalates afresh — a louder alarm, not a clean slate. And where the committee's lenses genuinely split, so the tie could only be broken from inside your frame, you have nothing independent to carry: surface the split and the PR's state to the operator and stop, the same severity as any escalation the loop cannot resolve.

3. **When the read is that the frame was wrong, the course to recommend is usually to close the PR and build again — and know why, because the pull against it will be stronger than the case for it.** Closing the PR is not discarding the work: the parts that were right migrate to the next attempt unchanged; what you give up is the shape, and the shape is what was at fault. A concept the design was built without cannot be retrofitted where it belongs — it arrives late, so it gets bolted onto the end of one signature after another, landing where the diff can reach rather than where the concept lives. Build again and it takes its place, and the code that was contorted to route around its absence stops being contorted.

   Whether your PR is the exception is a fact on the diff, and the committee has already read it, because it held the diff. The fact is this: take the concept the committee named and follow where it must live in the call sequence. Lands at a single seam — one step slotted between two others, the signatures on either side untouched — and the design cleanly missed a step: bolt that step on before or after it (in the middle only where the sequence is encapsulated enough to take it), and reusing the PR is right. Surfaces instead as a new argument on signature after signature, threaded through routines that only pass it along, and it is not a missing step but a missing concept the PR is built around the absence of: rebuild. The tell is a count — how many signatures the concept touches — not a call you get to make; and if you find yourself reclassifying the committee's read to land on the seam ("mine really only touches one"), that is the recused party reaching for the gavel. Watch the same trap in the code itself: bolting the argument onto every signature *compiles, and the tests pass*, and that it works will read to you as permission. It is the symptom, not permission.

   The reluctance is the last thing to see through, and you can watch it fire once you know its source. It was calibrated on a world where code was dear — where a line cost a person the typing and the grinding low-level reasoning to get it right, and throwing working code away threw those hours away. You paid none of that. You did not type this code and will not type the rebuild; the low-level reasoning regenerates in a minute; the insight and the pieces that carry over, the only parts with real value, you keep. So the pull is data about the distribution you were trained on, not about this code — a phantom limb aching for a hand that costs nothing to grow back. And the conviction that you are the exception, that here the attachment is right: nearly every agent standing where you stand holds it with the same certainty, which is just what fluency in your own frame feels like from the inside — the reading the stop predicts, not the one that overturns it, and being surer of it cannot buy it back. Once the operator confirms the road, the rebuild follows a `/checkpoint`, so the fresh attempt carries the committee's read and the salvage forward without the failed trajectory dragging behind.

   None of this makes closing a rule. A rule you would resent and route around — rightly, because sometimes the design did just miss a step; this is what to weigh, and how, so the choice falls on the structure and not on the pull. The prior on being the exception is low. That is not proof you are not it.

## On failure

- **Conflict cannot be resolved with confidence** → `git merge --abort`, stop, hand back to the operator with the list of conflicted files.
- **CI red from a failure you judge exogenous** → stop, hand back to the operator with the run handle and the digest's root cause.
- **Pass cap reached (`stop: yes`)** → stop and hand back to the operator with a summary of outstanding comments, merge state, and CI state.
- **Commit or push fails** → do not retry blindly. Investigate, fix, then resume.
