---
name: materialize
description: >
  Make a planned Premise real: implement, then land it. The thin entry — it
  Checkpoints the (often large) conversation so the implementation runs in a fresh
  context, then resumes into /_continue_materialize, which is the implementation
  skill proper. Composes /checkpoint; the actual work lives in the continuation.
---

# Materialize

Make a planned Premise real. By the time you reach `/materialize` the conversation that decided *what* to build can be enormous — a long check-in, a `/design` pass, a back-and-forth — and implementing while re-reading that whole conversation as a cache read every turn is the token leak this skill exists to stop. So `/materialize` does not implement in this conversation. It is a control handoff to the implementation body, and a handoff is where context is shed: it [Checkpoints](../checkpoint/SKILL.md) — sheds the conversation with a `/clear` — and resumes into `/_continue_materialize`, the implementation skill proper, running in a fresh context that carries only the Digest and the Carryover.

**When to use:** the same Premises `/_continue_materialize` handles — mechanical, CI-gated, or off-tree work where the plan is settled and the implementation is what remains. The split is invisible to the operator: you run `/materialize`; the implementation runs afterward in `/_continue_materialize`, once the checkpoint has handed off.

## Procedure

This skill is thin. Its whole job is to checkpoint into the implementation body, and the one thing it must get right is that the plan survives the clear.

### 1. Make sure the plan is in the Carryover

`/_continue_materialize` implements the committed approach — what `/design` produced, or what you and the operator agreed in this conversation. The `/clear` destroys this conversation, so that approach has to cross the clear in writing or it is gone. The checkpoint you are about to run writes the Carryover; when it does, the Carryover must carry the committed implementation plan — the design decisions, the contracts the tests will keep, the refactors the clean shape needs, the first concrete action — not a gesture at "the plan we discussed." This is the one piece only this conversation holds.

### 2. Checkpoint into the implementation body

Invoke `/checkpoint` via the Skill tool with the argument `_continue_materialize`. It has you read the Digest and author the Carryover (carrying the plan, per step 1), then — unless it refuses first — composes the Resume Brief, clears this session, and injects the Brief as the cleared session's first turn, closing into `/_continue_materialize`.

Invoking `/checkpoint` is the last thing this skill does. Inside it, the `vv checkpoint` call hands control to an external process that drives the clear and injects the Resume Brief that grounds the cleared agent and activates `/_continue_materialize`; that cleared agent — not you — does the implementation, CI, commit, PR, and the hand-off to `/parlay`. `/materialize` is finished once the checkpoint is invoked; you do not carry on into the implementation.
