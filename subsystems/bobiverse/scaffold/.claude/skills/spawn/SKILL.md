---
name: spawn
model: opus
effort: low
description: >
  Spawn a Bob on an existing Assignment. Takes an <ASSIGNMENT> id as input and
  delegates to `vv spawn`, the canonical composed spawn. Does not author
  anything; the Assignment must already exist.
---

# Spawn

Spawn a **Bob** (a secondary Claude Code session in a fresh worktree) to work an existing **Assignment**. The current conversation stays focused.

**When to use:** you have an Assignment ID already (freshly authored by `/file`, pulled from `/available`, or named by the operator) and you want a Bob to pick it up in its own worktree. When the Assignment doesn't exist yet, use `/file --spawn` (which authors a Premise and spawns a Bob on it in one call).

## Input

`/spawn <ASSIGNMENT>`: one Assignment ID per invocation. For bulk use (e.g., across the `/available` set), invoke `/spawn` once per Assignment. No batch mode; keeps the skill thin.

## Procedure

`/spawn` is a thin wrapper over `vv spawn`, the canonical composed spawn. Run it against the Assignment:

```bash
vv spawn <ASSIGNMENT>
```

That single call is the whole spawn. It preflights the Assignment against the per-Component pickability stack, resets the managed clones, resolves the target repo from the Assignment's prefix, forks the Component's **Foundation** so the Bob inherits the priming as conversation history, pre-seeds the worktree's Claude-Code folder-trust, and runs `workmux add --background` in the target repo with the Bob's agent command: auto-mode permissions, the `CLAUDE_CONFIG_DIR`/`VV_DATA_DIR`/`PATH` trio, and Remote Control named for the worktree. The worktree is named canonically `<lowercase-prefix>-<number>` (`BOB-108` → `bob-108`, `PM-45` → `pm-45`), so the prefix tag shows which repo the Bob is in and tmux window names don't collide across Components.

**Preflight is the gate.** Before creating anything, `vv spawn` refuses an Assignment that is not pickable: not in the Component its prefix names (`BOB-…` → BOB, `PM-…` → PM, etc.), Workflow not `Submitted`/`Returned` (refuses Resolved and Claimed), a (kind, Route) pair vaudeville-core's (kind → permitted-routes) constraint disallows: an unspawnable Type, or a Route the Type does not permit (a `Premise` may not be `direct`; a `Manual` carries no Route, and is refused only if it has one), or any inward dependency unresolved. The refusal is a one-line message on stderr with a non-zero exit; surface the line and stop. This is what makes `/spawn` the authoritative receiving-end gate when an Assignment arrives via cross-Component fanout from `/onward`: the peer's own prefix decides its pickability, not the caller's. The dep-blocked refusal (`<ASSIGNMENT> blocked by X, Y (unresolved)`) fires here, upstream of the Bob's existence; a Bob never spawns on a dep-blocked Assignment.

`vv spawn` exits non-zero for any of several reasons: a preflight refusal, an unknown prefix or a target repo missing on the host, no Foundation for the Component (run `vv prime <PREFIX>` first), a launcher/downstream failure, or a `workmux add` name collision. On any of these its stderr surfaces and the spawn aborts. Do not paper over a failure with a hand-rolled `workmux add`; the loud exit is intentional, and the whole point of routing through `vv spawn` is that there is one spawn path carrying the fork, the trust pre-seed, and the agent command.

### Report

Tell the operator:

- Assignment ID (`<ASSIGNMENT>`) and a one-line summary of what the Assignment is asking.
- Worktree name (`<lowercase-prefix>-<number>`) and the command to open it: `wm open <prefix>-N`.

Do not wait. The Bob works asynchronously.

## Non-goals

- **Does not author an Assignment.** The Assignment must exist. Use `/file` to author a Premise (pass `--spawn` to author and spawn in one call).
- **Does not implement.** `/spawn` only spawns; the cue downstream renders the Route-specific first-turn body, and the Bob realizes the Assignment through cue's `/realize`. Whether the Bob checks in before realizing is determined by the Assignment's Route (direct skips the chat gate; check-in waits for the operator).
- **Does not claim the Assignment.** The Bob's first-turn body claims via `vv assignment-claim`. Pre-claiming from `/spawn` would race the Bob's own claim and leave the State/Workflow bookkeeping in a confused state.
- **Does not check for existing worktrees.** That's workmux's territory; `vv spawn` surfaces `workmux add`'s name-collision refusal rather than pre-checking.

## Tips

- **One Assignment per `/spawn`.** For bulk use, invoke the skill repeatedly.
- **The Bob is the expert on its assignment after it thinks.** Expect pushback on the Assignment's framing. That pushback is the value.
- **Chat message ≠ file pointer.** The Bob's IC check-in goes in chat; the scratch stays in the scratch. "See `.scratch/thinking.md`" is a failed check-in.
