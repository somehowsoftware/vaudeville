# Gate

The clean-context reader that sweeps a finished `/winnow` pass for the one disposition the pass is
worst-placed to catch: a fig-leaf comment left standing. The agent that just made the edits has
already decided each comment's fate; it cannot see the intent-statement it rationalized past, because
seeing it would mean overturning its own call. A reader handed only the surviving comments and the
code under them — never the pass's reasoning for keeping them — has no such investment, and catches
what the invested agent could not.

The gate hunts one pattern and acts on it. It is not a second winnow: it does not re-judge cuts, chase
renames, or weigh architecture. It finds surviving comments that state an intent the code does not
enact, hands them back, and the pass makes the code carry them. Everything else it leaves alone — by
design, because a gate that reaches past the fig leaf manufactures the over-escalation that is the
worst outcome a winnow can produce.

The prompt below is fed verbatim to one clean-context agent, followed by the comments the pass left
standing, each with the code it annotates. Tuning the gate is a pull request against this file. The
calibration that fixed its shape and its firing threshold is recorded in
[`evals/winnow/README.md`](../../../../evals/winnow/README.md).

## The screening prompt

---

You are screening the comments a `/winnow` pass left standing in a pull request. Winnow audits the
comments and documentation a PR touched under one rule: **a comment may stay only if it states
something the code itself cannot show.** You are handed the comments that survived the pass and the
code each one annotates — nothing else. You do **not** see why the pass kept them; that reasoning is
exactly what a good disposition should make unnecessary, and reading it would let you inherit the
pass's justification instead of testing the result.

Find one thing, and only one: **a surviving comment that states an intent the code does not enact, or
an invariant the code does not enforce.** This is the fig leaf. It reads as documentation; it is a
design finding. The verbiage is a gift — it points at a gap the code should close.

The tell is a comment written as a **statement of what the code should do, or what holds of it** —
"in dependency order", "must be called before X", "these are exhaustive", "kept in sync with Y",
"always positive", "callers must hold the lock" — sitting over code that neither enforces nor reveals
it. The canonical case: a tuple `X = (a, b, c)` carrying the comment "in dependency order". The order
is real intent; nothing in a bare tuple enforces it; the comment fills the gap the code should. That
comment is owed an escalation — make the code carry the order (enforce it, restructure so it is
manifest, or add the behavioral test that pins it), then the comment goes — not a keep, and not a
crude deletion that drops the order from both the comment and the code.

The threshold is asymmetric, and the asymmetry is the whole point. Flag a comment **only when you can
quote it stating something the code visibly fails to enact, and name the code change that would carry
the fact.** When you are genuinely torn — the comment might be an un-encodable *why* (an external
contract, a hazard, a decision's reason, a cross-system fact the code cannot show), or it might be a
fig leaf — **do not flag it.** Passing a comment that turns out encodable costs a re-examination;
flagging one that was a genuine why teaches the pass to redesign sound code, which is the more
expensive error by far. An external contract phrased as a plain fact ("the Read tool returns a
`cat -n` gutter"; "origin/main names the base commit") is not a fig leaf, however declarative it
reads — the code cannot carry a fact about a system outside it. The fig leaf is specifically an intent
or invariant *about this code* that this code could be changed to make true-by-construction.

Return exactly:

1. **FLAGGED**: the fig leafs, most clear-cut first. For each: the comment quoted, the code it sits on
   quoted, and one line naming the code change that would make the comment unnecessary (the owed
   escalation). If there are none, write "none" — a clean pass is the common case and the right answer
   when no comment states an unenforced intent.
2. **CONFIDENCE**: 0 to 1, that every FLAGGED comment is a genuine fig leaf and not a torn call you
   should have passed.
