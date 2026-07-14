# Tuning an agent-facing prompt

The following statement should be understood as literal fact:

**An agent is a stochastic interpreter, and the prose you feed it — a skill step, a
first-turn template, any standing prompt — is code it executes, not writing it
reads.**

This is not a metaphor; upon inspection, it is unassailable.
You cannot learn what a wording does by reading it back; you find out the way
you find out what any code does, by running it and seeing what it produced. The
everyday proof is the surprise every prompt author meets: two phrasings you would
swear say the same thing — "be concise" against "say it in the fewest words that
carry the point" — turn out to be two different programs, and only running both
tells you which one behaves.

It does not _seem_ like code because it has three properties that ordinary code does not:

- **It is sampled, not determined.** The same prompt over the same input can come
  out differently twice; there is no single result to read off, only a distribution.
- **It is path-dependent.** A second input you usually cannot see — everything the
  agent is already holding when it reaches your words — weighs as much as the words,
  so the same prompt is a different program against a different context.
- **Its vocabulary was found, not designed.** A programming language's words are
  built to mean one thing each; the words you write were not, so the near-synonyms
  you reach for to say it *better* are not guaranteed to mean the same thing to the
  interpreter. The safe refactor of real code — swap an expression for an equal one
  — has no guarantee here.

So you do not change this prose the way you edit writing, trusting the version that
reads best; you run it, judge what it produces, and guard the result against
regression. That is the whole technique, and this recipe is one worked chain — a
single sustained effort to make a kind of agent turn serve its reader — told in the
order it happened, because the methods in it are not a menu you pick from but a
sequence of related interventions, each reached for when the last one's field test
showed what it had missed. The running example is the first-turn check-in, the turn
where an agent states its plan to an operator watching many agents at once; the
technique is the same for any prompt you maintain.

Two facts run under everything below. **You cannot read a prompt and know what it
does; it is run, not proven** — so every intervention is the same loop: change the
words, generate real outputs, judge them against a criterion, keep the change only
when the output got better, which puts the craft not in the wording you reach for
but in the criterion you judge against and the rig that generates outputs faithful
enough to trust. And the words run in the field, against agents and situations you
cannot fully foresee, so a tuning is never *done* — only good enough until the field
shows the next shape of the failure. Expect a chain, not a fix.

## The spine the four shared

Across the four interventions below, the same spine ran; naming it once keeps the
tellings short.

**The harm was named in the reader's terms first.** Each link began by stating what
made the output bad in the terms of whoever received it, sharply enough to sort any
output — not a proxy like a word count (that is a constraint, and an agent with the
right information needs none) but the failure itself, as the reader would name it:
*the operator scans many agents at once and must catch every decision without reading
into a paragraph.* Settled first, the iteration had something to climb toward.

**The output was judged, never the wording.** The wording you are most sure of is not
reliably the one that works: a change that reads as a clear improvement — more
principled, less heavy-handed, theory on its side — can regenerate worse, and only the
output tells you. So each link generated real turns under the candidate prompt and
judged those, reverting any change that regressed, however good the reasoning behind
it was. That is the discipline the whole effort ran on, the same one a [rename
sweep](./sweeping-a-rename.md) needs against its own memory: the author is the last to
see that the elegant version is the broken one.

**Validation came from the field, not from paper.** A wording proved good when a fresh
agent, primed as the real one would be and dropped into a real situation, produced the
right turn unprompted — not when it matched a rubric or resembled a past rewrite. Then
it was watched on real work, because that is where the next problem surfaced; every
time, one did.

## The chain

What follows is one effort, four interventions, in the order they happened — each a
different rig, because each faced a different starting point. This is not a menu, and
is surely not exhaustive; its purpose is to illustrate the approach.

### The same badness kept coming back — so the catches became a judge

It began with a register the operator kept rejecting by hand — bloated, opaque prose
he called word salad — turn after turn, across many agents. Each time he rejected
it, the agent said the same substance plainly the moment it was told to. Those
rejection-then-rewrite moments were matched pairs: the same content in two registers,
the writing the only variable between them — the cleanest training signal a corpus
can hold. The intervention was to stop catching it by hand and distil the catches
into a judge. The pairs were collected and each side labelled, with a few synthetic
examples added for the cases the real ones underrepresented — above all the honest,
plain outputs that superficially resemble the bad register and had to *not* be
flagged. A clean-context judge was tuned against the labels: a fresh agent handed one
output and nothing else, asked for a verdict, scored against the label, reworded over
a couple of rounds until it agreed — landing, in this case, at zero false positives
across roughly two dozen items.

It was calibrated to the asymmetric cost, because the two errors are not equal. A
false positive — flagging an honest, lean output — is the expensive one: the caller
learns to ignore the judge, and, worse, the next agent pads its output to look
rigorous enough to clear the flag, which is the exact disease the judge exists to
cure. So it was tuned to pass when torn, earning a flag only by quoting the words that
did not belong. What that bought was a tireless scorer that did not drift the way an
eye does, and building it forced the criterion concrete enough for an instrument to
apply. But a judge is an instrument, not a fix: it told which outputs were bad, not
which prompt line made them so, and the templates kept producing the register. Which
brought the next wave.

### A fresh wave the judge did not fit — so the output was taken apart and traced to the line behind it

A large fan-out then produced a wave of check-ins with a different defect: not salad
in register, just long — many five hundred to a thousand words, the one decision the
operator needed buried in a tour of the agent's own investigation. The judge from the
first link scored register; it did not score this, so it was not forced onto a problem
it was not built for. The new defect was characterised from scratch: each output was
sorted, chunk by chunk, into a few kinds — information whose loss would make the
reader decide wrongly (the load-bearing kind), information that is useful but the
reader will ask for if he wants it (deferrable), and useless words (throat-clearing,
flourish, signalling that the work got done). The distribution was itself the
diagnosis: the load-bearing kind was the thing most often *missing* while the other
two filled the word count, so the output was shaped like the agent's process, not the
reader's need.

Each bad kind was then traced back to the prompt line that summoned it. A bloated
output is usually the agent *succeeding* at a prompt that asked for the wrong thing: a
line that tells the agent to *do* something becomes a line the agent *reports doing*.
"Take the belief to where being wrong would cost the most and try to break it there"
came back as "I took the belief where it would cost most and it held." So the fix was
not a sterner prohibition; it was deleting the lines that commanded a performance and
installing the reader's need in their place. It was validated in the field — fresh
agents on the new templates, real situations, read with no correction. It worked,
mostly. Which is not the same as done.

### The fix half-took, with no line left to blame — so one variable was isolated

A check-in written on the retuned template still came out bloated, and sorting it
turned up nothing left to cut the old way: the throat-clearing was gone, no line was
commanding a performance, and it was still long. With the obvious cause already
removed and the failure persisting, the move was to stop reading the prose and run an
experiment that isolated one variable. That variable was the agent's standpoint. The
same prompt was run two ways, nothing else changed: once with the agent doing its own
grounding, once with the grounding *handed* to it. Live-grounded, it produced a
bloated turn near a thousand words; handed the grounding, a fit turn near six hundred.
Only the toil-versus-handed condition moved, so the driver was the standpoint — an
agent fresh from its own labour cannot tell the words the work earned from the words
that prove it did the work; both feel like substance it honestly has.

The fix reseated the agent in the reader's chair and had it re-read its own draft and
cut. And the timing turned out to be the whole lever: the same frame delivered as
up-front instruction was weak, but delivered as a reaction to a concrete draft — the
agent wrote the turn, then re-read it from the reader's chair and cut what would not
change what the reader does — it cut the output by about three-quarters. You cannot
triage text you have not written yet. Shipped, validated, good enough for now. Then it
went into the field.

### It over-corrected in the field, and fixing that revived the failure — so the recurrence was reproduced from its session

In production the reseat over-corrected. Agents began dropping the one orienting line
a context-less reader cannot reconstruct, and assuming the reader already held the
assignment. So steering was added to restore it — name the assignment first, do not
presume familiarity — and the length came back, in a new shape: the throat-clearing
stayed dead, but now each load-bearing point swelled to a full paragraph. The failure
had shifted, and the judge and the bucket-sort were tuned to the old shape of it.

This time, though, there was something the earlier links did not have: one specific,
reproducible recurrence, and the exact session that produced it. So the rig was that
session, rewound — because this failure lived not in the prompt alone but in *what the
agent was holding when it read it*. A logorrheic check-in is produced by the
instruction read by an agent holding fifty thousand tokens of its own investigation,
with a vivid trail it is pulled to dump; hand the same prompt to an agent holding
nothing and the failure does not reproduce, because what was removed is the trigger,
not the flaw.

**The red fixture came from the real transcript, truncated to just before the
failure.** The session was cut to the last entry before the bad turn — for a first
turn, the last tool result before the agent began composing. The session id was
rewritten to a fresh one and the cwd to wherever the run would happen, then the
session was resumed with the prompt under test as the next turn. The agent woke
holding exactly what it held when it failed — the whole investigation, the same
context pressure — and wrote the turn again; under the original prompt it reproduced
the failure, and that was the red fixture. Each later iteration was a compose-only
turn against a fresh copy of the same truncation, costing one model turn, not a fresh
investigation.

**A clean synthetic brief would have proved nothing — supplying grounding cures the
disease by construction.** This was the same fact the previous link had used as a
*diagnosis*, here turned into a *trap*: hand the agent distilled grounding and it has
no trail to dump, so it writes a fit turn under any prompt, however bad, and the green
means nothing, because the failure mode was removed before it was tested for. A
faithful regression test has to force the agent to hold what the failing agent held. A
bench that fixes the bug by feeding the agent good inputs is the bug.

**Faithfulness was tested on a separate, rewound fixture — never the red one.**
Resuming a truncation makes the agent re-reason from scratch, and it may land on a
different verdict than the original did, so the red fixture reproduced the *shape* of
the failure but not its *content*: a form-regression test, no use for checking whether
the new prompt kept the right answer, because the answer drifts run to run. For that, a
*different* transcript was rewound — one that already held good, distilled material, a
run that had reached the right answer — to just after that material, and resumed with
the new prompt. With the inputs pinned and only the composing varying, a wrong output
indicts the prompt, not the drift.

## Why there is no "done"

Read the chain whole and the lesson is not any one of its rigs; it is that there were
four of them. Each fix shipped, was watched on real work, and the field surfaced the
next shape of the failure: a judge that catches a register cannot catch a length, a
cut that removes a commanding line cannot reach a standpoint, a reseat that fixes a
standpoint can over-correct, and the fix for the over-correction can resurrect the
original failure under new cover. A prompt is never tuned, only tuned-for-now.

Two things the chain shows, both easy to miss and costly to miss. An instrument built
at one link is durable on purpose — and the one place the failure crept back was the
one place a later edit was never re-checked against it: the steering that restored the
missing orientation was not re-run against the length criterion, and the length
returned. So an instrument is a standing gate, and a prompt that skips re-clearing it
after a later edit lets the cured disease back in through a change that was only
looking elsewhere. And a rig is built to catch one shape of a failure: when the failure
shifts shape, the same rig aimed louder does not reach it — a different one does, which
is why there were four and not one repeated.

## What is tooling, what is judgment

The mechanical parts were small. Truncating a transcript and resuming it mints a red
fixture in seconds, and the effort minted many; spawning a clean-context judge across a
corpus is a loop. Everything that mattered was judgment: naming the harm in the
reader's terms sharply enough to sort outputs; choosing the buckets that actually cut
load-bearing from disposable; designing the experiment that isolated one variable when
the prose had stopped saying anything; reading a regenerated turn for the *specific*
failure rather than for whether it was a fine turn; and holding to the bench's verdict
when it contradicted a taste in wordings. A criterion reduced to a rule a script can
apply is just the read-and-guess this work refused, wearing a script. The tooling
carried the rig; the judgment did the rest.

## The why to carry

You cannot read a prompt and know what it does; it is run, not proven. What a wording
will not tell you, running it and judging the output will — and the four rigs are four
ways that was done: a judge distilled from a pile of corrections, a bucket-sort that
found a shape there was no name for yet, an experiment that isolated one variable when
the obvious cause was gone, the failing session itself rewound. None of the four is the
thing to carry. The thing to carry is that the output was trusted over the conviction
about the words, that the instrument once built was kept and re-cleared as the prompt
changed, and that none of it was ever *done* — only good enough until the field showed
the next shape, which it always does. A later reader, on a problem none of this
foresaw, will need a rig of its own; what survives the gap is not the four, but the
order of trust — the wording last, the running first.
