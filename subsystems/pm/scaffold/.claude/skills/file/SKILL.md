---
name: file
description: >
  Author a Premise in the tracker, in this thread. When a Premise has been
  worked out in conversation, the current agent composes the humble-snapshot
  description directly and files it via `vv file`. Pass `--spawn`
  to also spawn a Bob on the filed Premise.
---

# File

Author a **Premise** in the tracker from the current conversation. `/file` is the *deliberated* posture: the Premise has come out of a worked-through discussion, confidence is earned, and the current agent composes the full humble-snapshot description in this thread and files it.

**When to use:** the Premise is the product of a careful conversation — a design settled, a follow-up whose shape is understood, a backlog item you can frame in domain terms right now. The operator chose `/file` because the work is worked out; you are the in-thread branch of their classifier.

**When not to use:**
- The operator has *not* worked the concern out — it is a side-thought to capture provisionally. Use `/tangent`, which fills the deterministic `vv tangent` form instead of composing.
- The Premise already exists and you only want a Bob on it. Use `/spawn <PREMISE>`.

## Authoring posture

You are authoring a humble Premise snapshot in the frame doctrine sets out — read [[premise-frame]] for the authority. The reader will be a peer being briefed: more current information than you, the operator at their elbow, the ability to cross-check your framing against the code. What they will not have is this conversation. Your job is to carry the slice of it they will need, and to be honest about what you saw and where your confidence runs low.

The body has space for a short **framing** of what the work is (domain terms, no tracker references), the **relevant context** (what was decided, the constraint you think matters most — situational over prescriptive), the **assumptions the proposition rests on** (the title states what the author wants to be true; the body admits those wants stand on assumptions, named so the reader is free to question them — this is the step a user story leaves untaken), and the **disagreements and open questions** you noticed (the parts where your confidence runs low earn their place, because the reader will not otherwise know to ask).

The body does **not** contain acceptance criteria of any kind, confident specifications of mechanism, full conversation transcripts, or tracker references that double-book the dependency graph. Acceptance criteria are the sharp one: the reader treats them as a contract regardless of the hedges around them. Anti-pattern. Do not write them.

## Procedure

### 1. Compose the title — state the proposition

The title — the Premise's one-line `summary` — comes first, before the body. A **Premise** is *a proposition under which a change might be worth making*: a condition the author holds true and worth acting on, offered to a reader who is free to question the assumptions under it. The title is that proposition reduced to a phrase — what the author wants to be true, with the *how* and the *whether* left to the reader.

Composing it first is the forcing function, not a formatting preference: a proposition you can reduce to a phrase is proof you have thought the rationale through. If it will not reduce, the thinking is not finished — stay here until it does, rather than filing a placeholder and deferring the thought to the body.

The tell that you have a proposition and not a renamed ticket is that the title reads as a claim someone could disagree with, not an instruction to carry out. "Fix the worktree leak on claim failure" is a command and "worktrees shouldn't leak" is its negation; "The spawn path leaks worktrees when a claim fails" is the proposition under them — the thing the author believes is true and worth acting on. A title in the imperative voice or framed as a negation is the tell that the work is still held as a task to execute rather than a premise to examine; restate it as what you believe to be true.

The proposition still carries the scope. Load-bearing qualifiers — scope words, phase markers — belong in it, so the reader inherits the boundary the decision drew rather than a silently widened one.

### 2. Compose the body and the rest

With the title fixed, write the rest:

- **The description body**, in the shape above.
- **The target Managed Repository** — which project prefix the work lands in (`PM`, `BOB`, `CORE`, …). The Premise files under that project, which need not be the one cwd sits in.
- **The Route** — `direct`, `check-in`, `plan`, or `manual`: the lifecycle the work expects. If unsure, `check-in` is the safe default; its failure mode is a conversation that was not strictly needed.
- **The Depend edges**, if any — the resolved-prerequisite Premises this one waits on. One `--dep` per edge.

### 3. File it

Carry the summary and description through single-quoted heredocs so backticks and other shell metacharacters in the body do not interpolate:

```bash
summary=$(cat <<'PREMISE_SUMMARY'
<the title from step 1 — the proposition, qualifiers verbatim>
PREMISE_SUMMARY
)
description=$(cat <<'PREMISE_BODY'
<the humble-snapshot body>
PREMISE_BODY
)
new_id=$(vv file --project <PREFIX> --summary "$summary" --description "$description" --route <ROUTE> [--dep <PEER>...])
```

The single-quoted delimiters (`'PREMISE_SUMMARY'`, `'PREMISE_BODY'`) are load-bearing — they tell the shell to take the body literally, with no command substitution and no variable expansion. Each closing delimiter sits at column 1 with no leading whitespace, or the heredoc will not close. `vv file` prints the new Premise's idReadable to stdout.

### 4. Spawn, if `--spawn` was given

If the operator invoked `/file --spawn`, spawn a Bob on the Premise just filed:

```bash
vv spawn "$new_id"
```

`vv spawn` is the canonical composed spawn (bobiverse, via the `vv` facade): it cuts the worktree and seeds the Bob, which claims the Premise on its own first turn. Without `--spawn`, stop after filing — the Premise waits in the pickup pool for a later `/spawn` or `/available`.

### 5. Report

One line: the new Premise id and its Route, and — if you spawned — the `wm open <prefix>-N` for the new worktree (`vv spawn` reports the canonical `<lowercase-prefix>-<number>` name). If you only filed, note the Premise is in the pickup pool.

## Non-goals

- **Does not capture provisionally.** `/file` composes a worked-out Premise. Provisional capture is `/tangent`.
- **Does not claim or work the Premise.** Filing leaves it Submitted in the pickup pool; a spawned Bob claims it on its own first turn.

## Tips

- **One Premise per invocation.** Don't batch.
- **Topic ≠ summary.** Compose the structured summary, description, and Route from the conversation; do not paste the operator's prose in as the body.
