from __future__ import annotations

# The Brief's opening line, single-sourced so the Digest extraction can recognise a
# Brief that a reseat seeded as the fresh session's born-grounded first turn (it arrives
# as a typed user turn) and refuse to read it back as the operator speaking.
RESUME_BRIEF_OPENING = "# Resume Brief: you are a Bob, mid-work, just past a Checkpoint"

_GROUNDING_FRAME = (
    RESUME_BRIEF_OPENING
    + """

Your previous session was reseated: its oversized conversation shed and this
fresh session born in its place. This message is the whole handoff. You are not
a new agent and this is not a restart: the worktree, the branch, and the diff
are exactly as you left them; what is gone is everything that existed only as
talk. Read this Brief top to bottom, in order; the order is essential.

A freshly grounded context does not present as ignorance; it presents as
fluency. You will meet familiar-shaped terms below and feel that you know them.
That feeling is the failure mode, not evidence against it: before you lean on
any doctrine or domain term, re-read its definition from its source on disk.

## 1. The operator's turns: the Digest

Ground here first, before your own notes. These are the operator's turns,
verbatim and in order, extracted mechanically from the session transcripts.
Nothing here is summary, and nothing here is yours, and that is exactly why it
governs: your Carryover below and your own memory both came from the context
that was just shed, but the operator's words did not. So these turns are the
standing account of what this work is and why. Rebuild your understanding on
them, and read whatever you find next (a command's output, the code, a file,
the history) against this account; where what you find fights it, that clash is
the signal to surface, not a licence to drop the operator's word for the fresher
reading. The Digest is cumulative
across this Bob's checkpoints: one section per session in the chain, each headed
with that session's transcript, and within it each turn headed with the lines it
spans in that transcript. Where a turn's meaning leans on what surrounded it (a "yes, do
that" with no antecedent, a reaction to a tool result), follow its line locator
into the named transcript and read the neighborhood; never fill the gap with
what is plausible, and never surface one of your own pre-reseat replies as though
the operator said it. Read to the end: an early instruction can be revised or
reversed by a later turn, and the latest turn is the live one.

"""
)

_CARRYOVER_FRAME = """\

## 2. Your Carryover

You wrote this, minutes ago in wall-clock time and a whole context ago in every
way that matters, against the Digest above. Trust its synthesis (that is the
one thing only the shed conversation could have built) and treat its pointers
as essential: where it names a source, re-read the source rather than
recalling it. It is still your own note, though, and downstream of the operator's
turns above: where the two disagree, the turns are the account, not your
synthesis. Where the Carryover and the worktree disagree (a step marked done
the diff says isn't), the worktree wins; note the discrepancy, reconcile, and
continue. Do not re-plan finished work, and do not re-open decisions the
operator's turns above already settled.

"""

_CONTINUE_BARE = """\

## 3. Continue

Resume mid-stride: take the next concrete action the Carryover names, in this
worktree, now. Do not ask the operator what to do when the Carryover already
names it; the Checkpoint exists so this moment needs no rescue. But the
operator's turns above are still the account: if the first thing you check comes
back against what they established (the tracker, the code, or the history saying
otherwise), surface that clash before you act on it, rather than letting the
fresher reading quietly stand in for the operator's word. And continuing
grants no new license: the reseat changed your context, not your authority. If
the next step is outward or irreversible and the operator's turns did not
already authorize it, carry the work to that edge, surface, and wait.
"""

_CONTINUE_LIFECYCLE = """\

## 3. Continue

You checkpointed on the way into a lifecycle skill; its body carries the
procedure for the work ahead. Invoke the Skill tool with skill `{continuation}`
now; grounded by this Brief, it picks up mid-stride. As it runs, the operator's
turns above stay the account: if something you check comes back against what they
established, surface that clash before acting on it. Continuing grants no new
license: the reseat changed your context, not your authority.
"""


def resume_brief(digest: str, carryover: str, continuation: str | None) -> str:
    closing = (
        _CONTINUE_BARE
        if continuation is None
        else _CONTINUE_LIFECYCLE.format(continuation=continuation)
    )
    return _GROUNDING_FRAME + digest + _CARRYOVER_FRAME + carryover + closing
