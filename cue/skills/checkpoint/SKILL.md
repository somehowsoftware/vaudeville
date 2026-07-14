---
name: checkpoint
description: >
  Shed an oversized conversation mid-work without losing the thread. Print the
  Digest with `vv digest` and read it, author the Carryover curated against it,
  then end the turn by delivering the Carryover to `vv checkpoint`, which
  composes the Resume Brief and reseats this session in place, replacing it with a
  fresh session born holding the Brief as its first turn. Lifecycle skills pass their continuation as this
  invocation's argument; bare /checkpoint resumes straight into the work. The
  invoking turn must end at the `vv checkpoint` call; everything after it is
  wiped.
---

# Checkpoint

A conversation deep into real work eventually weighs more than it carries. `/checkpoint` sheds it without dropping the thread: read the operator's verbatim turns, author the Carryover holding what only this conversation built, and hand your own pane to a detached reseat that replaces this session with a fresh one born holding everything the resumed you needs: as your first turn, already in context, nothing to fetch. What comes back is not a new agent and not a restart: it is you, minus the conversation, mid-stride in the same worktree.

This is the standalone primitive, invokable mid-work in any assignment. It is also the mechanism the realization procedures and `/parlay` reuse: each crosses into its continuation by invoking `/checkpoint` with that continuation named. **The continuation is the skill named as this invocation's argument, without the leading slash (for example `_continue_full_process`); invoked bare, there is none, and the resumed you continues the work directly.** Call it CONTINUATION in the steps below.

Three steps, in order. The third ends this conversation, so everything that should survive must be in the Carryover when it runs.

## 1. Read the operator's turns

```bash
vv digest
```

The Digest prints into this conversation: the operator's turns, verbatim and in order, across every session of this Bob, each turn headed with the lines it spans in its session's transcript. Read it before you write a word of the Carryover. Your memory of this conversation has already drifted: at this depth of context, the ask you remember best is the one with the most repetition behind it, not the latest one the operator gave, and a late revision or reversal is exactly what a flattened memory drops. Curate against the operator's actual words, not your recollection of them. Where a turn's meaning leans on what surrounded it (your reply it was answering, a tool result it reacted to), its line locator names the spot in the transcript; follow it rather than fill the gap from memory.

## 2. Author the Carryover

You're about to shed this conversation. Everything said here (the operator's asides, your own reasoning, every definition you absorbed along the way) vanishes at the reseat. What survives without your help: the repository, the doctrine on disk, the session transcripts, and the Digest you just read; the reseat seeds the Digest into your first post-reseat turn alongside the Carryover you author now. What survives only if you write it down is the part only this conversation built: the synthesis (the understanding you'd otherwise re-derive: why the approach is shaped the way it is, what you tried, ruled out, and why), the open edge (the exact seam where finished work stops and unfinished begins), and the next concrete action (what your post-reseat self does first, specific enough to start doing rather than start planning).

Write for the post-reseat reader. They are not a stranger and not a fool: they wake holding this same Digest and your Carryover, with the whole repo and the whole doctrine tree on disk. What they lack is everything that existed only as talk, and they will not *feel* the lack. A reseated context does not present as ignorance; it presents as fluency. Your post-reseat self will meet a familiar-shaped term and produce a confident, plausible, wrong account of it without noticing the moment of invention. The Carryover is your one defense, and the defense is not better prose: it's pointers.

So divide the load by where things already live. The operator's words sit in the Digest, re-injected before your Carryover is read, so a decision's provenance needs no re-narration: your paraphrase is exactly the surface a false memory grows on, while the operator's own turns can't drift. Where a particular moment matters, the Digest's line locator is its address; point at it rather than retell it. Definitions live in the doctrine: a term your next action leans on gets the path to where it's defined, not a gloss. Code state lives in the worktree; the diff will still be there.

One kind of thing has no home to divide onto: a conclusion *you* reached. An architectural fork you resolved, a shape you committed to, an option you weighed and ruled out, these live in none of the durable places. Not the Digest: that is the operator's words, and the operator stating a problem is not you settling it. Not the doctrine, not the diff. A conclusion the conversation alone reached is the one thing with no address to point at, which makes it the one thing you must carry whole: not the verdict alone, but what closed it and why it is closed rather than still open.

Failure shapes to write against, each a recognizable shape rather than a rule:

- The carried fact. Storing in prose what already lives somewhere durable: a paraphrased decision, a glossed definition, a re-narrated history. Prose drifts between writing and reading; the Digest, the doctrine, and the repo don't. Where a sentence could be wrong, a path cannot. Store the path.
- The status report. A Carryover that describes the work from above: accurate, orderly, unactionable. Your post-reseat self reads it, nods, and has to re-plan anyway. The checkpoint's job is the next stride, not the view.
- The confident gloss. Defining a framework term in your own words because the definition feels obvious right now. Right or wrong, a gloss reads identically, and the post-reseat reader will trust it precisely because you wrote it. The path to the definition forces the re-read; the gloss forecloses it.
- The uncorrected memory. A Carryover authored before the Digest is read, curated against the remembered ask instead of the actual one. It will be fluent, orderly, and aimed at a version of the work the operator already revised away, and everything downstream of the reseat inherits the drift. Step 1 comes first precisely so this drift gets caught while it still can be.
- The stripped conclusion. The mirror of the carried fact, and the subtler error: where the carried fact stores something durable as prose, this stores something that exists *only* as prose as a bare verdict. A decision you reached (not one the operator handed you) recorded as its outcome with the reasoning that closed it left behind. The operator's decisions survive without your help, verbatim in the Digest; a conclusion you reached has only this Carryover, and stripped of its grounding a verdict reads identically to a question still open. Your next self, handed a verdict it cannot defend, re-opens it, and may decide it the other way, against the option you had already rejected. So for a conclusion you closed: mark it closed, name what closed it (your own reasoning, a panel, a read of the code, with the path to that grounding where it has one), and keep the reasoning that holds it settled. This is the one place the pointer-not-prose rule inverts: a fact shrinks to a pointer because it lives elsewhere; a conclusion the conversation alone reached must carry its own defense, because nothing else will.

The test for done: imagine waking with only this Carryover and what it points at. If your first move would be to re-plan, you've written a status report. If your first move would be to assert a *fact* the Carryover only asserts (one that lives in the Digest, the doctrine, or the diff), you've stored a fact where a path belonged. If your first move would be to re-decide something you had already closed, you carried the verdict but not the reasoning that holds it. If your first move is the next concrete action, taken with the right referents under your feet, it's ready.

## 3. Reseat and resume, and stop

Deliver the Carryover you authored as the stdin of the one call that does everything else:

```bash
vv checkpoint --resume CONTINUATION <<'CARRYOVER'
<the Carryover, exactly as authored>
CARRYOVER
```

Omit `--resume` entirely for a bare checkpoint. Before anything irreversible happens, `vv checkpoint` refuses (and you fix and retry) if the continuation skill is not deployed, the Carryover is empty, or this session's transcript cannot be resolved. Otherwise it persists the Digest and the Carryover, composes the Resume Brief from them, and launches the detached reseat.

**This command is where the skill ends. Running it hands control to an external process (a detached reseat, outside this conversation) that performs everything that remains, on its own:** it replaces this pane's session in place with a fresh one born holding the Resume Brief (the Digest, the Carryover, and the instruction for what comes next) as its first turn. The replacement, the grounding, and the continuation are the reseat's to deliver and a freshly-reseated agent's to carry out. None of it is yours, and there is nothing for you to wait for.

So the skill is complete the moment you invoke the command. **Produce nothing after it**: not a summary, not a sign-off, not a "checkpoint launched," not one more tool call. There is no next step for you: the reseat replaces this session whole, whatever it is mid-doing, so the Carryover was your last word and you have already delivered it. Run the command; stop.
