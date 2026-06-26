# Premise Frame

A Premise is the unit of cross-time, cross-agent communication in Vaudeville. Author and reader are both ephemeral agents; the conversation that produced the Premise is unavailable to the agent that picks it up.

## What a Premise is

A point-in-time snapshot of what one limited-perspective, fallible voice understood about a piece of work when writing it down. By read time, the surrounding code, specs, and situation may have moved. The human is available after the prep to clarify and decide; the Premise need not anticipate every question.

The reader is a peer being briefed on a situation, not a worker receiving instructions: read the Premise, read the surrounding code, form your own judgment, surface any disagreement before proceeding. The Premise gives situational awareness, not orders.

## What the Premise is not

Not a contract. The author cannot specify good output in advance; the situation reveals it as work progresses, and the reader's judgment is part of the process.

Not a list of [acceptance criteria](../vocabulary.md#acceptance-criteria). The reader, trained on human-style PM artefacts, treats acceptance criteria as the contract regardless of surrounding hedges; the reflex is downstream of training and cannot be repaired at the reading end, so the only place to correct is the author side. Do not author them.

Not the conversation that produced it. Dumping the full conversation makes the Premise too long to be useful and gives the reader no clue what mattered. The author's job is to identify the slice of context the reader will actually need.

## What to put in a Premise

A Premise has space for:

- **A short framing of what the work is.** One or two paragraphs, in domain terms, no tracker references.
- **The relevant context.** What was decided in conversation; what assumptions are in play; the author's view of the most important constraint. Bias toward the situational, away from the prescriptive.
- **What the author was guessing they would accept, if noted.** A fallible note the reader need not honour. Optional, often best omitted: if the author can genuinely sketch the work's disposition, the sketch belongs in the framing, not under a heading that invites the reader to anchor.
- **Disagreements and open questions the author noticed.** Things the author was unsure about; things the human flagged but did not resolve; parts where the author's confidence runs low. The reader will not otherwise know to ask about them.

A Premise does *not* have space for:

- Full conversation transcripts. Extract the slice; do not dump.
- Confident specifications of mechanism. The reader chooses the mechanism.
- Acceptance criteria of any kind. See above.
- Tracker references that duplicate the graph. `X depends on Y` or `X is a subtask of Z` restates what the tracker already carries; the graph is the single source of truth. References that give coloring context (a lesson from a prior Premise, reasoning history, anything the graph cannot carry) are welcome.

## How to read a Premise

Treat the Premise as evidence of what one prior voice thought, not as truth. Cross-check against current code, specs, and surrounding work before anchoring on its framing. If Premise and code disagree, the code is the authoritative tiebreaker; the Premise is provisional.

Surface substantive disagreement to the human before proceeding; such disagreement is data, not failure. A wrong framing that surfaced disagreement early has done its job; a Premise the reader silently followed into wrong work has failed even if its framing was technically defensible.

## How this document gets revised

When a Premise authored to this frame produces a check-in that goes off the rails (the reader anchored on something misleading, the situational awareness was insufficient, or the reader treated part of the Premise as a contract), revise this document. The frame is itself a humble snapshot and does not exempt itself from its own discipline.
