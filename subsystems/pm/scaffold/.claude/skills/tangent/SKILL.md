---
name: tangent
description: >
  Capture a side-concern as a provisional Premise without working it out.
  The current agent fills the deterministic `vv tangent` form (the operator's
  prompt verbatim plus possibly-relevant context) and that files a provisional
  Premise. Pass `--spawn` to also spawn a Bob on it.
model: opus
effort: low
---

# Tangent

Capture a **tangent** (a side-concern the operator wants off their plate without working it out) as a provisional Premise. `/tangent` is the *thin-signal* posture: there is nothing yet to author, only to capture, so the current agent fills the deterministic `vv tangent` form rather than composing prose. The form composes a provisional body from the fields and files it.

**When to use:** the operator raised a concern but has *not* worked it out: a "we should look at this someday," a worry surfaced mid-task that would derail the current thread, anything where composing a full Premise would mean inventing direction the operator did not give. The operator chose `/tangent` because they know they are in the thin-signal case.

**When not to use:**
- The Premise *has* been worked out and full composition is earned. Use `/premise`.
- The Premise already exists. Use `/spawn <ASSIGNMENT>`.

## The discipline: fill, do not author

A tangent is a *capture*, not a composition. The `vv tangent` form has fixed fields and no slot for discretion; that is deliberate, and your job is to fill them faithfully, not to improve on them:

- **`--prompt`** is the operator's original ask, captured **verbatim**. Do not paraphrase, generalise, or relocate the qualifiers that carry the meaning. The prompt is the fixed source of truth the reader checks every other field against.
- **`--context`** is *observations only*: what you noticed in the conversation or the code that might be relevant. Not recommendations, not proposed fixes, not a remedy. If you find yourself writing what *should* be done, you have crossed from capture into authoring; stop.
- **`--summary`** is a one-line restatement in the operator's words, qualifiers verbatim.
- **`--dep`** wires any resolved-prerequisite edges.

You do not choose the Component. `vv tangent` **classifies** which Component the captured concern belongs to from its subject; the thread you captured it in is exactly the wrong default, and the classifier exists to take that decision off you. Pass **`--project <PREFIX>`** *only* to override the classification when the target is already settled (the operator named it, or you are re-filing a known misfile); leave it off and let the classifier decide.

`vv tangent` fixes the Route to `check-in`, marks the body provisional, and classifies the Component; you set none of the Route, the body, or (by default) the Component. The form does.

## Procedure

### 1. Fill the form

Carry the summary, the verbatim prompt, and the context through single-quoted heredocs so backticks and other shell metacharacters in the operator's text do not interpolate; every operator-derived field is verbatim, so every one rides the safe pattern:

```bash
summary=$(cat <<'TANGENT_SUMMARY'
<one-line restatement, qualifiers verbatim>
TANGENT_SUMMARY
)
prompt=$(cat <<'TANGENT_PROMPT'
<the operator's ask, verbatim>
TANGENT_PROMPT
)
context=$(cat <<'TANGENT_CONTEXT'
<observations only: no recommendations, no fixes>
TANGENT_CONTEXT
)
new_id=$(vv tangent --summary "$summary" --prompt "$prompt" --context "$context" [--dep <PEER>...])
```

The single-quoted delimiters are essential: they take the body literally, with no command substitution and no variable expansion. Each closing delimiter sits at column 1 with no leading whitespace. Add `--project <PREFIX>` only to override the classification. `vv tangent` prints the new Premise's idReadable to stdout.

### 2. Spawn, if `--spawn` was given

If the operator invoked `/tangent --spawn`, spawn a Bob on the tangent just filed:

```bash
vv spawn "$new_id"
```

`vv spawn` is the canonical composed spawn (bobiverse, via the `vv` facade). Without `--spawn`, stop after filing; the provisional Premise waits in the pickup pool for later triage.

### 3. Report

One line: the new Premise id, that it was filed provisionally, and, if you spawned, the `wm open <prefix>-N` for the new worktree (`vv spawn` reports the canonical `<lowercase-prefix>-<number>` name).

## Non-goals

- **Does not author.** No composed framing, no worked-out direction, no remedy. If the concern deserves that, it is a `/premise`, not a `/tangent`.
- **Does not claim or work the Premise.** A spawned Bob claims on its own first turn; an unspawned tangent waits in the pickup pool.

## Tips

- **The provisional banner is the form's, not yours.** `vv tangent` marks the Premise provisional and quotes the captured fields so none of the operator's text is read as authored structure. You add no hedges of your own.
- **One tangent per invocation.** Don't batch.
