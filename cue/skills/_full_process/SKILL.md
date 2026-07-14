---
name: _full_process
description: >
  Machinery, not a human command: the full-process procedure the /realize router
  dispatches to. Runs a Design pass as a matter of course (warm, before the
  clear), then checkpoints into _continue_full_process, the cold
  implementation body.
---

# Full process

[`/realize`](../realize/SKILL.md) dispatches here for full-process: the orderly-contribution procedure that carries an assignment from a settled goal to a tendered pull request. It runs the warm half now (the Design pass, which wants the rich context you are holding), then checkpoints into the cold implementation body, [`_continue_full_process`](../_continue_full_process/SKILL.md).

## Procedure

### 1. Run the Design pass

Invoke [`/design`](../design/SKILL.md) via the Skill tool. It consults `/panel`, commits to a design across the three axes (the domain terms, the interaction with existing code, the contracts the tests will keep) and surfaces that committed design. Run it as a matter of course: full-process does not make the Design pass optional, which is what moves the design-versus-implementation-detail confusion that sinks so many PRs from review time to the cheaper design time. (This is the opening half of the **Doctrine Bracket**; its closing half re-reads the design Doctrine against the diff, cold, in `_continue_full_process`.)

### 2. Checkpoint into the implementation body

Invoke `/checkpoint` via the Skill tool with the argument `_continue_full_process`. It has you read the Digest and author the Carryover (which must carry the committed design, because the clear destroys this conversation and the cold body implements from the Carryover, not from talk that no longer exists), then composes the Resume Brief, clears this session, and resumes into `/_continue_full_process`.

Invoking `/checkpoint` is the last thing this skill does: the cleared agent, not you, does the implementation, the closing half of the Doctrine Bracket, and the hand-off to Tender.
