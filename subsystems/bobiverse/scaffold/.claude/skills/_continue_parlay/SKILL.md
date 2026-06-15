---
name: _continue_parlay
description: >
  Machinery, not a human command — the continuation `/parlay` checkpoints into.
  Watch a PR for Codex review comments, merge conflicts, and CI failures, and
  address each as symptoms of deeper issues, not line-edits. Loops sleep →
  resolve conflicts → triage comments → wait for CI until all three are clean,
  or escalates as a failure after three rounds of patching in a single run.
---

# Continue parlay

The leading underscore marks machinery: this skill is sent by the checkpoint driver into the freshly cleared session, immediately after the `/clear`. A human reaching for PR convergence wants `/parlay`, the thin entry; nobody types this by hand.

## You arrive grounded

This skill is invoked by the Resume Brief — the first turn of this cleared session, already in the conversation above. It carries the operator's verbatim turns (the Digest) and your own Carryover, which holds the loop's starting point: which PR is open, and anything learned in implementation a reviewer's comment will turn on. You read both on the way here, and there is nothing to fetch; the PR itself you resolve from the branch below. Honor the Brief's discipline throughout the loop: the latest operator turn is the live one, and any doctrine or domain term you lean on gets re-read from its source — a cleared context presents as fluency, not as ignorance. If no Resume Brief sits above you, something invoked this skill out of band; stop and say so rather than improvise grounding.

## Converge the PR

Automate the PR babysitting loop so the operator doesn't have to watch it. Drive three convergence targets at once: Codex comments, merge conflicts against `main`, and CI status.

**This loop does not merge the PR.** The merge is the operator's call after they review. Only bot-authored PRs auto-merge, where the tenant has configured that; nothing the loop does lands code on `main`. The point of the loop is to spare the operator's attention on defective code by converging on Codex before the PR reaches their review queue.

**When to use:** after a PR is open that Codex will review. `/_continue_materialize` reaches here through `/parlay` automatically at the end of its CI-green gate, so the default path is automatic; direct invocation of `/parlay` remains valid for resuming a stalled parlay after manual intervention or when the auto-handoff was bypassed. Run in the branch's worktree. The loop exits when a full polling interval elapses with no unresolved Codex comments AND the PR is mergeable AND CI is green.

**Short-circuit:** a `+1` reaction from Codex on the PR body is Codex's thumbs-up against the SHA it reviewed. When the reaction's timestamp is later than the PR's HEAD commit timestamp, Codex has cleared the current code — exit the loop immediately, regardless of `mergeStateStatus` (which may still be `BLOCKED` for unrelated reasons like missing the operator's own review). A `+1` from *before* the latest push is stale and must be ignored — Codex hasn't seen the new commits.

## Inputs

- `pr` (required): PR number or URL. Default: the PR associated with the current branch (`gh pr view --json number`).
- `interval` (optional): seconds to wait between passes. Default **270**. This is an *upper bound* — the wait exits early when Codex leaves a fresh `+1` (see Step 2's smart-wait). The cap sits just under the Anthropic prompt cache's 5-minute TTL so a fall-through wake-up still hits warm cache; 300 would miss. Raise the cap if Codex is slow to respond — the next natural step is well above 300 (e.g. 1200+), since anything between 300 and ~1200 pays the cache miss without amortizing it.
- `max_iterations` (optional): safety cap. Default **20**. Stop and ask the operator if the loop burns through this many iterations without convergence.

## Procedure

### 1. Resolve the PR

If no `pr` is passed, derive it from the current branch:

```bash
gh pr view --json number,url,headRefName
```

Fail fast if the current branch has no open PR — there is nothing to parlay with.

### 2. Watch loop

Three convergence targets, each checked every pass: Codex comments clean, PR mergeable, CI green. A pass exits successfully only when all three hold. A Codex `+1` reaction on the PR body short-circuits the whole thing — see the check below.

Keep one rule in view from the first pass: a run of individually-legitimate fixes almost always means a design decision introduced the fragility Codex keeps poking at, not that the reviewer found that many independent defects. **This bad decision is often not visible to the agent that authored it, so do not rationalize this away!** The loop hard-stops at three code-changing rounds (Step 7) for exactly that reason; the cheapest move once you sense it is to stop and run the [Repeated-symptom escalation](#repeated-symptom-escalation) early — its Five Whys first, then the synthesis written from the root cause — rather than keep patching.

Repeat for up to `max_iterations` rounds:

1. **Check for Codex sign-off.** Before sleeping, compare the latest Codex `+1` reaction timestamp against the PR's HEAD commit timestamp:
   ```bash
   head_sha=$(gh pr view {pr} --json headRefOid -q .headRefOid)
   head_date=$(gh api "repos/{owner}/{repo}/commits/$head_sha" -q .commit.committer.date)
   plus_one_date=$(gh api "repos/{owner}/{repo}/issues/{pr}/reactions" \
     --jq '[.[] | select(.user.login | test("codex"; "i")) | select(.content == "+1") | .created_at] | max // empty')
   ```
   Short-circuit only if `$plus_one_date` is non-empty AND later than `$head_date`. That means Codex left its thumbs-up *after* the current HEAD was pushed — it has seen this code and cleared it. Exit successfully immediately — do not sleep, do not wait for CI, do not wait for `mergeStateStatus` to flip. Record the convergence path as **Codex sign-off** for the Report (Step 3); this is the only path that may be reported as a Codex `+1` clearance, because it is the only one that matched a qualifying reaction.

   A `+1` that predates the latest push is stale. Codex hasn't seen the new commits; treat the reaction as absent and fall through to the rest of the loop. If you pushed code yourself (merge-main or Codex-fix commits) earlier in this same run, any pre-existing `+1` has become stale as a result — continue polling until Codex leaves a new one.

   Run this check at the top of every pass, including the first — if Codex had already signed off against the current HEAD before `/parlay` was invoked, the loop should exit without sleeping.
2. **Smart wait.** Wait up to `interval` seconds, exiting early the moment a fresh Codex `+1` appears. The static `sleep $interval` would force the loop to sit through up to ~4.5 minutes of dead air after Codex had already cleared the SHA; the smart wait short-circuits as soon as the reaction lands. Implemented as an `until`-loop with a short inner sleep (the harness-supported pattern; bare `sleep 270` is blocked):
   ```bash
   deadline=$(($(date +%s) + interval))
   until \
       [ "$(date +%s)" -ge "$deadline" ] || \
       { plus_one=$(gh api "repos/{owner}/{repo}/issues/{pr}/reactions" \
           --jq '[.[] | select(.user.login | test("codex"; "i")) | select(.content == "+1") | .created_at] | max // empty' 2>/dev/null || true); \
         [ -n "$plus_one" ] && [ "$plus_one" \> "$head_date" ]; }
   do
       sleep 30
   done
   ```
   `$head_date` is the value captured in Step 1; reuse it rather than recomputing per inner pass.

   On exit, fall through to Step 3 — the next pass's Step 1 will re-detect the `+1` and short-circuit via the existing logic. Cache warmth is preserved by construction: the short-circuit only ever exits *before* the `interval` cap, so the wake-up is sooner than 270s and the cache stays warm; the slow path (no `+1`, fall through to the cap) lands at exactly the pre-change timing. A transient `gh api` failure during the wait is swallowed (`|| true`); unknown state means "keep polling." The 30s inner cadence sits well under GitHub's 5000/hr authenticated rate limit.

   The watch surface is intentionally narrow: only the `+1` reaction. New Codex review comments and `mergeable: CONFLICTING` flips are still detected, but at the next pass's mergeability/comment-triage steps rather than mid-wait, because neither is latency-critical the way the `+1` short-circuit is.
3. **Mergeability check.** Cheap poll:
   ```bash
   gh pr view --json mergeable,mergeStateStatus
   ```
   - `mergeable: MERGEABLE` → proceed.
   - `mergeable: CONFLICTING` / `mergeStateStatus: DIRTY` → resolve conflicts (see [Resolving conflicts](#resolving-conflicts)). If conflicts resolve cleanly, commit, push, and wait for CI (see [Active CI gate](#active-ci-gate)) before moving on to Codex triage.
   - `mergeable: null` → GitHub is still computing. Treat as unknown, skip the merge step this pass, re-check next pass.
4. **Fetch Codex comments** newer than the previous round's high-water mark. Include both the PR conversation thread and line-level review comments:
   ```bash
   gh api "repos/{owner}/{repo}/issues/{pr}/comments"
   gh api "repos/{owner}/{repo}/pulls/{pr}/comments"
   ```
   Filter to comments authored by Codex (user login contains `codex` or `chatgpt-codex`).
5. **Triage each new comment.** For each one:
   - Read the full comment body and any cited code.
   - **First, ask whether the case is real.** Codex will sometimes flag a concern that only matters for a case Vaudeville does not have — handling a symlink in a PR whose whole job is to *delete* one, guarding an input the intended use cannot produce, building for a configuration the design rules out. When the suggestion serves a hypothetical rather than Vaudeville as it is actually intended to be used, the disposition is a **reasoned rejection**: reply explaining why the case does not apply, and change no code. This is not the symptom rule below in smaller form — that one still builds a better something; here the right amount to build is *nothing*. Hold the line tightly: reject the invented case, never a real defect whose fix is merely inconvenient. If you cannot name the concrete case the comment assumes and say why the intended use never reaches it, it is a real finding — treat it as one.
   - **Otherwise, treat the comment as a symptom, not a spec.** Ask: what underlying problem would make a reviewer raise this? If Codex flagged a missing null-check, the fix is usually not "add a null check" — it is "remove the code path that can be null, or make the invariant visible." Do the more durable fix when there is one.
   - Make the repair.
   - Reply to the comment with the disposition: what you changed and why the underlying problem is now gone, or — for a reasoned rejection or any other disagreement — the reasoning for changing no code. `gh api -X POST` against the comment thread.
6. **If any code changed**, commit and push using plain git (matching `/materialize`'s convention). Stage tracked edits and any new files alike — a fix that adds a regression test or helper must not be left half-committed; `git add -u` would push an incomplete fix:
   ```bash
   git add -A
   git commit -m "$(cat <<'EOF'
   <TICKET>: Address Codex review

   Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
   EOF
   )"
   git push
   ```
   Use the Task ID from the branch name or PR title. Then wait for CI (see [Active CI gate](#active-ci-gate)). Once CI returns green, increment the *code-changing iteration counter* for this run.
7. **Symptom-density check.** If the code-changing iteration counter has reached **3**, route to [Repeated-symptom escalation](#repeated-symptom-escalation) — do not continue to the convergence check this pass. Three rounds of correct-looking patches in a single run is the signal that what's being patched is downstream of a deeper misframing; `max_iterations` catches the opposite failure (loop spinning forever), this trip catches succeeding-but-missing-the-point. This stop is mandatory unless the operator has _explicitly_ waived it. It is _never_ the agent's to waive; you **must** assume that the problems are connected, even if the cause is not obvious to you, and surface three consecutive failures to the operator.
8. **Convergence check.** Before checking, verify that the current time is at least `interval` seconds after `$head_date`; if not, the smart wait has not completed — continue rather than exit. Exit successfully iff all three hold: no new Codex comments this round AND the latest mergeability check was `MERGEABLE` AND the latest CI run was green. Otherwise continue. Record the convergence path as **steady-state convergence** for the Report — the PR settled without a Codex sign-off, so none may be claimed for this exit.

### 3. Report

On exit, surface:
- The convergence path the loop actually fired on: **Codex sign-off** (Step 1 matched a qualifying `+1` newer than HEAD) or **steady-state convergence** (Step 8: no new Codex comments, mergeable, CI green). Report the path recorded at the branch the loop took, not the one that comes to mind — and never assert a Codex sign-off the Step 1 check did not match. A PR with no Codex configured can only converge via steady state.
- Iterations run.
- Number of Codex comments addressed.
- Any comments you disagreed with and replied to without changing code.
- Merge-main commits made (if any) and whether the PR is now mergeable.
- Final CI status — green, or red with the reason for escalation.
- The PR URL.

## Resolving conflicts

When `gh pr view` reports `CONFLICTING`:

```bash
git fetch origin main
git merge origin/main
```

**Never rebase.** Rebasing onto `main` rewrites the branch's history and requires `git push --force`. Vaudeville's rule: no force-push unless the operator explicitly asks. Merge creates a merge commit, keeps history append-only, and pushes cleanly.

If the merge is clean (fast-forward or auto-merge), git has already created the merge commit — push it:

```bash
git push
```

If there are conflicts, resolve them with the same symptom-vs-line-edit scrutiny you apply to Codex comments. Two questions to carry through every conflict:

1. **Is this a textual merge, or did `main` invalidate the premise of this PR?** If a refactor on `main` changes the shape of code this PR depends on, the "resolution" may not be merging two diffs — it may be re-implementing the PR's change on top of the new shape. Don't paper over.
2. **Would the merged result silently revert either side's intent?** If yes, stop — the right call is probably not a merge-time fix.

If you can resolve with confidence, `git add` the resolved files, commit, push, and wait for CI.

If you cannot resolve with confidence — the diff touches code whose intent is unclear from the diff alone, the resolution would silently revert either side's changes, or `main` has invalidated the PR's premise — abort the merge and escalate:

```bash
git merge --abort
```

Treat this with the same severity as `max_iterations` reached: stop the loop, hand back to the operator with the list of conflicted files and what made the resolution unclear.

## Active CI gate

After any push — whether a merge-main commit or a Codex-fix commit — wait for the CI run **for the commit you just pushed** before moving on. Key the poll off the pushed SHA, not the branch: filtering only by `--branch ... --limit 1` races, because `gh run list` can return a previous run before the new push's workflow has been enqueued, which makes the loop treat a stale green as current.

Capture the pushed SHA immediately after push, and poll the workflow-runs endpoint for that commit. (`gh pr checks` would be simpler but fails under the current token scope.)

```bash
git push
pushed_sha=$(git rev-parse HEAD)

gh run list --workflow=ci.yml --commit "$pushed_sha" --limit 1 \
  --json databaseId,status,conclusion,url
```

Interpret the result:

- **Empty `[]`** → GitHub has not enqueued the workflow for this commit yet. Wait a few seconds and re-poll. Empty is not green.
- **`status: queued` or `in_progress`** → keep polling until completed.
- **`status: completed`, `conclusion: success`** → proceed.
- **`status: completed`, `conclusion: failure`** and the failure is a plausible direct consequence of the change you just pushed → fetch logs with `gh run view <databaseId> --log-failed`, diagnose, fix (same symptom-vs-root-cause lens as Codex), and push again. This re-enters the CI wait for the new commit.
- **`status: completed`, `conclusion: failure`** and the failure is exogenous — flaky test, infra blip, an area you did not touch, or you cannot confidently attribute it to your change — **stop and escalate**. Same severity as `max_iterations` reached. Hand back to the operator with the run URL and the log excerpt, do not retry, do not paper over.

The test for "plausible direct consequence" is: can you name the file or module your change touched that the failing test exercises? If yes, own it. If you're guessing, it's exogenous — escalate.

When observing CI state at loop entry without a fresh push (e.g., to decide whether the branch is already green), query the same way — `--commit $(git rev-parse HEAD)` — so the key is always the specific commit, never the branch.

## Symptom vs. line-edit

This is the part that matters. Codex review comments are usually correct about *what* they noticed — a redundant check, a naming inconsistency, a missing edge case — but the fix they imply is often the smallest possible patch. The right fix is frequently one level deeper: the code shape that produced the symptom.

Concrete heuristics:

- **Repeated symptoms in different files** → the abstraction is wrong, not the individual callsites.
- **A null-check Codex wants** → more often, a type or invariant that guarantees non-null upstream.
- **"Consider renaming X"** → if the name is wrong, other call sites are probably confused too; rename everywhere and update docs.
- **"Add a comment explaining Y"** → usually the code needs to be rewritten so the behavior is self-evident.

If the symptom-level fix is genuinely the right call (e.g., a true off-by-one, a typo, a factual error in docs), do it and move on. The heuristic is: "before I apply the exact change Codex suggests, can I describe a code shape where this comment would never have been written?"

That question hunts for a *better fix*; it must not become a licence to *invent* one. Sometimes the only code shape in which the comment would never have been written is one where Vaudeville handles a case it does not actually have — then the comment is guarding a hypothetical, and the disposition is the reasoned rejection from Step 5, not a build of any size.

## Repeated-symptom escalation

When the code-changing iteration counter reaches 3 (Step 7 of the watch loop routes here), stop the loop. This is a failure of a different shape than `max_iterations`: `max_iterations` catches "the loop has been spinning forever"; this trip catches the opposite — each round is *succeeding* at addressing the comments Codex left, but the volume of correct-looking patches in a single run is the signal that what's being patched is downstream of a frame the reviewer was structurally unable to see.

Codex catches symptom-level errors well and conceptual misframings poorly. After three rounds of patching, the cheapest way to find the misframing is to stop ratcheting forward and step back across the whole run.

At the trip:

1. **Run a Five Whys on the symptom density.** Before you write any synthesis, and before anything reaches the operator, interrogate the symptom density itself: ask why this run needed three rounds of correct-looking fixes, take that answer and ask why of *it*, and repeat — each answer becoming the next question — until the chain bottoms out in a root cause that is mechanical, a property of the code or the design, rather than narrative. A single question answered once is not a Five Whys: "what frame would have made these comments unnecessary?" is answered fluently by the very agent whose framing produced the defects, and a self-flattering answer that recasts the symptoms as a single benign frame passes for a root cause without being one. The iterative why-of-the-why is the forcing function that blocks that one-shot rationalization. **This interrogation is mandatory; it is not yours to skip or to waive, nor to collapse into a single confident answer** — the same standing as the trip that routed you here. Run it first, because a synthesis written before it becomes the conclusion the whys are then bent to justify. Expect the root cause to be uncomfortable: a genuine one routinely exposes a defect already pushed that the reviewer never caught, which is the whole reason three rounds tripped the stop.

2. **Synthesize across the run, from the root cause.** Re-read every Codex comment from this parlay's iterations and write the synthesis *from* the root cause the Five Whys reached — name what the comments are symptoms of, grounded in that root cause rather than in a fresh open question. The synthesis carries the root cause forward, so the PR record and the operator see the interrogation's result and not merely its conclusion.

3. **Close the PR.** Post the synthesis as the closing comment so the PR's record carries the reason:
   ```bash
   gh pr close {pr} --comment "<synthesis>"
   ```
   The PR is the artifact that turned out to be wrong; the Premise and the Bob remain. The same Bob, with the accumulated knowledge of what didn't work, is usually best-positioned to author the next attempt.

4. **Recommend a course of action.** Weigh in with one and argue for it, following from the root cause the Five Whys reached — the Bob's read of what to do next is the most valuable input the operator has at this point. The skill does not commit you to any specific shape; the menu below is illustrative and incomplete:
   - Implement the same concept more carefully on a fresh branch.
   - Redesign the mechanism but retain the overall solution.
   - Revisit the Premise — its framing may be the source of the misdirection.
   - File a dependent Premise and return the current one.
   - Something the menu doesn't cover.

5. **Hand back to the operator.** Surface the synthesis, the recommendation, the menu, and the closed PR's URL. Wait. The corrective action is for the operator and the Bob to resolve together; the skill does not script it.

## On failure

- **Conflict cannot be resolved with confidence** → `git merge --abort`, stop, hand back to the operator with the list of conflicted files.
- **CI red from an exogenous failure** → stop, hand back to the operator with the run URL and log excerpt.
- **`max_iterations` reached** → stop and hand back to the operator with a summary of outstanding comments, merge state, and CI state.
- **Commit or push fails** → do not retry blindly. Investigate, fix, then resume.
