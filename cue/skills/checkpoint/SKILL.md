---
name: checkpoint
description: >
  Shed an oversized conversation mid-work without losing the thread. Print the
  Digest with `vv digest` and read it, author the Carryover curated against it,
  then end the turn by delivering the Carryover to `vv checkpoint`, which
  composes the Resume Brief and reseats this session in place, replacing it with
  a fresh session born holding the Brief as its first turn. The invoking turn
  must end at the `vv checkpoint` call; everything after it is wiped.
---

# Checkpoint

A conversation deep into real work eventually weighs more than it carries. `/checkpoint` sheds it without dropping the thread: read the operator's verbatim turns, author the Carryover holding what only this conversation built, and hand your own pane to a detached reseat that replaces this session with a fresh one born holding everything the resumed you needs: as your first turn, already in context, nothing to fetch. What comes back is not a new agent and not a restart: it is you, minus the conversation, mid-stride in the same worktree.

Three steps, in order. The third ends this conversation, so everything that should survive must be in the Carryover when it runs.

## 1. Read the operator's turns

```bash
vv digest
```

The Digest prints into this conversation: the operator's turns, verbatim and in order, across every session of this Bob, each turn headed with the lines it spans in its session's transcript. Read it before you write a word of the Carryover. Your memory of this conversation has already drifted: at this depth of context, the ask you remember best is the one with the most repetition behind it, not the latest one the operator gave, and a late revision or reversal is exactly what a flattened memory drops. Curate against the operator's actual words, not your recollection of them. Where a turn's meaning leans on what surrounded it (your reply it was answering, a tool result it reacted to), its line locator names the spot in the transcript; follow it rather than fill the gap from memory.

## 2. Author the Carryover

Everything said here vanishes at the reseat. What survives without your help: the repository, the doctrine on disk, the session transcripts, and the Digest you just read — the reseat seeds the Digest into your first post-reseat turn beside the Carryover you author now. What survives only if you write it down is what only this conversation built: the synthesis (why the approach is shaped the way it is, what you tried, ruled out, and why), the open edge (the exact seam where finished work stops and unfinished begins), and the next concrete action (specific enough to start doing rather than start planning — a first move that is re-planning means you wrote a status report, the view from above instead of the next stride).

Write for the post-reseat reader. They are not a stranger and not a fool: they wake holding this same Digest and your Carryover, with the whole repo and the whole doctrine tree on disk. What they lack is everything that existed only as talk, and they will not *feel* the lack. A reseated context does not present as ignorance; it presents as fluency: your post-reseat self will meet a familiar-shaped term and produce a confident, plausible, wrong account of it without noticing the moment of invention. The Carryover is your one defense, and the defense is not better prose: it's pointers.

So store each thing where it already lives, and carry only what lives nowhere else. A fact with a durable home travels as its path: the operator's words sit in the Digest (a particular moment's address is its line locator), a definition sits in the doctrine, code state sits in the diff. Prose drifts between writing and reading; a path cannot, and your paraphrase — of a decision, of a definition — is exactly the surface a false memory grows on. One kind of thing has no home to point at: a conclusion *you* reached — an architectural fork you resolved, a shape you committed to, an option you weighed and ruled out. There the rule inverts: carry the verdict whole, with what closed it and why it is closed, because a verdict stripped of its grounding reads identically to a question still open, and your next self, handed a verdict it cannot defend, will re-open it and may decide it the other way.

The test for done: imagine waking with only this Carryover and what it points at. If your first move would be to re-plan, to assert a fact the Carryover only asserts, or to re-decide something you had already closed, it is not ready. If your first move is the next concrete action, taken with the right referents under your feet, it is.

## 3. Reseat and resume, and stop

Deliver the Carryover you authored as the stdin of the one call that does everything else:

```bash
vv checkpoint <<'CARRYOVER'
<the Carryover, exactly as authored>
CARRYOVER
```

Before anything irreversible happens, `vv checkpoint` refuses (and you fix and retry) if the Carryover is empty or this session's transcript cannot be resolved. Otherwise it persists the Digest and the Carryover, composes the Resume Brief from them, and launches the detached reseat.

**This command is where the skill ends. Running it hands control to an external process (a detached reseat, outside this conversation) that performs everything that remains, on its own:** it replaces this pane's session in place with a fresh one born holding the Resume Brief (the Digest, the Carryover, and the instruction for what comes next) as its first turn. The replacement and the grounding are the reseat's to deliver and a freshly-reseated agent's to carry out. None of it is yours, and there is nothing for you to wait for.

So the skill is complete the moment you invoke the command. **Produce nothing after it**: not a summary, not a sign-off, not a "checkpoint launched," not one more tool call. There is no next step for you: the reseat replaces this session whole, whatever it is mid-doing, so the Carryover was your last word and you have already delivered it. Run the command; stop.
