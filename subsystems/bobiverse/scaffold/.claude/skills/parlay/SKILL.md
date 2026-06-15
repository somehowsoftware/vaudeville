---
name: parlay
description: >
  Watch a PR for Codex review comments, merge conflicts, and CI failures, and
  address each as symptoms of deeper issues. The thin entry — it Checkpoints so the
  long convergence loop runs in a fresh context, then resumes into
  /_continue_parlay, which is the convergence loop proper. Composes /checkpoint.
---

# Parlay

Watch a PR to convergence — Codex comments, merge conflicts, CI — and address each as a symptom, not a line-edit. The convergence loop is long and runs many turns; running it while re-reading the whole conversation as a cache read every pass is the token leak this skill exists to stop. So `/parlay` does not run the loop in this conversation. Control has been handed to parlay — typically from `/_continue_materialize` at the end of implementation, sometimes by the operator resuming a stalled run — and a control handoff between lifecycle skills is where context is shed: it [Checkpoints](../checkpoint/SKILL.md), sheds the conversation with a `/clear`, and resumes into `/_continue_parlay`, the convergence loop proper, running in a fresh context.

This is the second clear in a materialize→parlay run, and it is not "materialize also clears before parlay" — it is here *because control was handed to parlay*. Each lifecycle skill that takes control sheds the context the previous one accumulated; the implementation conversation is large by the time the PR is open, and the convergence loop has no use for it.

**When to use:** after a PR is open and Codex will review it — the same situation `/_continue_parlay` handles. `/_continue_materialize` invokes `/parlay` automatically at the end of its CI-green gate, so the default path is automatic; direct invocation remains valid for resuming a stalled parlay.

## Procedure

This skill is thin. Its whole job is to checkpoint into the convergence loop.

### 1. Make sure the loop's starting point is in the Carryover

`/_continue_parlay` resolves the PR from the current branch, so it needs little from this conversation — but the `/clear` destroys whatever this conversation does hold. When the checkpoint writes the Carryover, the Carryover should carry the loop's starting point: which PR is open, that CI was green at hand-off, and anything learned in implementation a reviewer's comment will turn on. Keep it to what the loop cannot re-derive from the branch.

### 2. Checkpoint into the convergence loop

Invoke `/checkpoint` via the Skill tool with the argument `_continue_parlay`. It has you read the Digest and author the Carryover (per step 1), then — unless it refuses first — composes the Resume Brief, clears this session, and injects the Brief as the cleared session's first turn, closing into `/_continue_parlay`.

Invoking `/checkpoint` is the last thing this skill does. Inside it, the `vv checkpoint` call hands control to an external process that drives the clear and injects the Resume Brief that grounds the cleared agent and activates `/_continue_parlay`; that cleared agent — not you — runs the convergence loop, the conflict resolution, the symptom-density escalation, and the final report. `/parlay` is finished once the checkpoint is invoked.
