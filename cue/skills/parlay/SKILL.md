---
name: parlay
description: >
  Watch an assignment's open PRs (one, or several when the work shipped as
  coordinated PRs across repositories) for Codex review comments, merge
  conflicts, and CI failures, addressing each as a symptom of a deeper issue.
  The thin entry: it Checkpoints so the long convergence loop runs in a fresh
  context, then resumes into /_continue_parlay, the convergence loop proper.
  Composes /checkpoint.
---

# Parlay

Watch an assignment's open PRs to convergence (Codex comments, merge conflicts, CI) and address each as a symptom, not a line-edit. Usually that is one PR; when an assignment produced coordinated PRs across repositories, it is the whole set, converged against the same targets so the operator says it once rather than invoking parlay per PR. The convergence loop is long, so `/parlay` does not run it in this conversation: it [Checkpoints](../checkpoint/SKILL.md), sheds the conversation with a `/clear`, and resumes into `/_continue_parlay`, the convergence loop proper, in a fresh context. Control reaches parlay typically from [`_tender`](../_tender/SKILL.md) at the end of a procedure's carry-to-PR piece with the single PR it opened, sometimes from the operator naming a set or resuming a stalled run.

**When to use:** after a PR is open and Codex will review it (the same situation `/_continue_parlay` handles). `_tender` invokes `/parlay` automatically at the end of its CI-green gate with the single PR it opened, so the default path is automatic; direct invocation (naming one or several PRs) is how an assignment's coordinated PRs get babysat together and how a stalled parlay is resumed.

## Procedure

This skill is thin. Its whole job is to checkpoint into the convergence loop.

### 1. Make sure the loop's starting point is in the Carryover

`/_continue_parlay` defaults to the PR on the current branch, so a single-PR parlay needs little from this conversation, but the `/clear` destroys whatever this conversation does hold, and a multi-PR set is not re-derivable from the branch at all. When the checkpoint writes the Carryover, the Carryover should carry the loop's starting point: which PR or PRs are open (naming each explicitly when the assignment produced coordinated PRs across repositories), that CI was green at hand-off, and anything learned in implementation a reviewer's comment will turn on. Keep it to what the loop cannot re-derive from the branches.

### 2. Checkpoint into the convergence loop

Invoke `/checkpoint` via the Skill tool with the argument `_continue_parlay`. It has you read the Digest and author the Carryover (per step 1), then (unless it refuses first) composes the Resume Brief, clears this session, and injects the Brief as the cleared session's first turn, closing into `/_continue_parlay`.

Invoking `/checkpoint` is the last thing this skill does; the cleared agent, not you, runs the convergence loop, the conflict resolution, the symptom-density escalation, and the final report.
