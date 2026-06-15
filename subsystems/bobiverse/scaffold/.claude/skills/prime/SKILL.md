---
name: prime
model: sonnet
effort: low
description: >
  Refresh a Managed Repository's Foundation — the primed Claude Code session future
  Bobs fork from. Drives the priming turns (cross-context Doctrine, the
  tenant's project context, then the Managed Repository's own docs) against a fresh
  CC session and records the new session id. Takes an optional project prefix;
  without one, primes every Managed Repository.
---

# Prime

Each Managed Repository has a **Foundation**: a Claude Code session primed with the cross-context Doctrine, the tenant's project context, and the Managed Repository's own spec and UL. Every Spawn into that Managed Repository's worktrees forks from the Foundation, so new Bobs inherit the priming as their conversation history instead of skimming a CLAUDE.md block. This skill creates or refreshes Foundations.

**When to use:**

- The Doctrine or the tenant's project context has changed (anything under `~/.vaudeville/doctrine/` or `~/.vaudeville/project-docs/`), so the existing Foundations' priming is stale.
- A Managed Repository's spec or UL has changed in a way that should flow into the priming.
- Spinning up a new tenant: the host has projects registered in `~/.vaudeville/projects.toml`, but no Foundations yet.
- An operator suspects a Foundation is drifting (recent Bobs from that Managed Repository missing context they should have inherited) and wants a clean re-prime.

**When not to use:**

- For everyday work. Priming is deployment-time / refresh-time, not per-Bob.
- For a Premise-specific seed prompt — that's rendered by the spawn-time downstream (`vv premise-context`), not here.

## Procedure

### 1. Choose scope

`/prime <PREFIX>` re-Primes a single Managed Repository. The prefix is one of the project prefixes in `~/.vaudeville/projects.toml` (e.g., `BOB`, `CORE`, `PM`, `RING`, `CUE`, `HOOK`).

`/prime` with no argument re-Primes every Managed Repository in the order `vv prime` returns them. This is the redeploy path.

### 2. Run

```bash
vv prime [<PREFIX>]
```

The command opens a fresh `claude` session in each Managed Repository's main clone, runs the priming turns, and writes the new session id to `~/.vaudeville/foundations.toml`. Each turn is a real Claude Code one-shot invocation; expect each Managed Repository to take long enough that the operator should not be staring at the terminal waiting.

On failure (a missing `claude` binary, a non-existent main clone, a non-zero `claude` exit), the command surfaces the error and stops. Partial state may have been written — `vv prime <PREFIX>` for the affected Managed Repository is the recovery move.

### 3. Verify

```bash
cat ~/.vaudeville/foundations.toml
```

A successful Prime writes one line per Managed Repository mapping the prefix to its new session id. Confirm the targeted prefix is present (or all prefixes, in the redeploy case).

## Non-goals

- **Does not modify the Managed Repository.** The Foundation's transcript lives in Claude Code's session storage, not in any repository under operator-managed source control.
- **Does not spawn Bobs.** The Foundation sits idle until a `/spawn` into the Managed Repository forks from it.
- **Does not check Doctrine freshness.** The operator decides when to re-Prime; the skill doesn't compare timestamps or guess staleness.
