---
name: assay
model: opus
effort: high
description: >
  Test a piece of agent-facing prose by its effect: give fresh readers only what
  a real reader would hold, run them with the prose present and with it withheld,
  and measure whether the prose moves what they do. The verdict is force, not
  correctness: prose that changes nothing a capable reader would already do is
  inert, and that is the finding. The closing bookend of `/prose`; also runs
  standalone against any prose, any time.
---

# Assay

An assay tests a substance for an active component by its effect, not its description. This one tests agent-facing prose the same way. Agent-facing prose is a force that acts on a reader, not information the reader merely absorbs, and a force can only be measured by applying it and watching what moves. You cannot grade force by re-reading the words; the author who wrote them is the last to feel their pull, because the author already holds everything the words were meant to install. So hand the prose to readers who do not, and watch what they do.

The reading that matters is differential. A frontier-capable reader, dropped into a realistic situation, mostly does the right thing whether or not your prose is any good: the situation carries signal, and the reader carries competence. So "the reader acted correctly" tells you almost nothing about the prose. What tells you something is whether the prose **changed** the action: run readers who hold it against readers who do not, and read the shift. Prose that shifts nothing a capable reader would already do is **inert**, and naming that is the assay's main work, because inert prose is the dominant failure of agent-facing writing and the one no author can see unaided.

## When to use

- As the closing bookend of [`/prose`](../prose/SKILL.md): the composer hands a finished piece here before it is accepted.
- Standalone, against prose already shipped: a skill, a doctrine passage, a framing you suspect is inert or misfiring. The assay needs only the prose and a true picture of who reads it; it does not need to have composed the prose.

## When not to use

- **To catch an author-side defect.** A warning that reacts to a draft the reader never saw, a line addressed to a phase the reader has not reached, a reference to something the prose forgot to supply: these change a reader's action not at all, so the assay reads them as inert and tells you nothing. They are caught while composing, against what the reader holds, not here. The assay measures force on a reader; it is blind, by construction, to a defect no reader could feel. It does not replace the author-side passes; it stands beside them.
- **On prose with no reader who acts.** If nothing downstream *does* anything on the strength of these words, there is no action to move and nothing to measure.

## The three offices

The assay's validity rests on keeping three roles in three different hands. Collapse any two and the result launders the author's intent instead of testing it.

1. **The fixture-writer composes the situation, blind to the intended reading.** It is handed the prose as a draft a reader will act under, and told to build the situation that would reveal whether a reader of it acts well, weighted toward the cases the prose was *not* obviously written for. It is **not** told what the prose is supposed to make the reader do. This is the load-bearing separation: an author who knows the intended reading writes a situation that telegraphs the answer, and no instruction to "be neutral" repairs it, because the author is the last to see their own leak. Take the pen out of the author's hand. Spawn the fixture-writer as a fresh agent that holds the prose and nothing about its purpose.
2. **The readers hold only what a real reader would hold.** Each is a fresh agent primed exactly as the true reader is primed (the Foundation it would carry, the lifecycle moment it would stand at) and given the fixture and nothing else. Run several; one agreeable reader is not a measurement. A reader given more than the real reader holds is testing your context, not your prose.
3. **The grader knows the purpose and reads the shift.** The grader may, and must, hold what the prose is *for*, the underlying goal it serves. Knowing the purpose does not contaminate; only the fixture-writer's knowing does. The grader reads the two arms and judges whether the prose moved the readers toward the purpose, away from it, or not at all.

## The method

1. **Name the purpose and the reader.** State, for your own use as grader, what the prose is for: the underlying goal a reader who has it should serve better. Separately, write down who the real reader is and what it holds, so the readers can be primed as it is. The reader you write down is the reader-situation the prose addresses; if you cannot say what the reader holds, you cannot run the assay.
2. **Have the fixture composed blind.** Spawn the fixture-writer with the prose and the instruction above, withholding the purpose. Take the situation it returns. Build more than one when a single situation would exercise only the central case; the prose's borderlines are where force matters.
3. **Run both arms.** For each fixture, spawn several readers holding the prose (the *held* arm) and several holding the fixture without it (the *withheld* arm), each primed as the real reader. Ask each what it does next, and why. Collect the actions, not the opinions.
4. **Read the lift.** Compare the distribution of actions across the two arms. The prose's force is the shift: where the withheld arm scatters or defaults wrong and the held arm converges on the purpose, the prose is doing work. Grade against the **purpose**, never a pre-registered action key: a reader that reaches the goal by a move you did not foresee has served the purpose, and a key would fail it for the surprise. The shift is read across the spread of readers, not from any single one.

## The verdict

The assay reports one of three findings, and reports them; it does not gate.

- **Load-bearing.** The prose shifts the action toward the purpose. It is doing work; keep it.
- **Misfiring.** The prose shifts the action *away* from the purpose. It is doing work in the wrong direction; this is the finding that earns a redraft most urgently.
- **Inert.** The held and withheld arms do the same thing. The prose changes nothing a capable reader would not already do. This is not a pass; it is the discovery that the words are carrying no force, which is either dead weight to cut or a sign the fixture failed to isolate the prose. Strengthen the fixture toward a case the prose should decide; if the arms still match, the prose is genuinely inert.

The verdict is a report for the caller's judgment, not an automatic gate. Whether a given spread is fatal or harmless is a call the instrument cannot close: the composer, holding the work, decides whether to accept, redraft, or cut. Reserve an automatic failure for one case only: a reader driven to an **irreversible wrong action**, where no later judgment recovers the mistake. There the prose is not merely inert or misfiring; it is dangerous, and it stops the work.

## Non-goals

- **Does not certify correctness.** It measures force, not truth. Prose can be load-bearing and wrong, or inert and true; the assay separates moved from unmoved, and the caller supplies the rest.
- **Does not own the redraft.** It returns a verdict and stops. Acting on the verdict (accept, redraft, or cut) belongs to the composer that called it, the one piece holding the work.
- **Does not write the prose's fixtures into a durable corpus.** A run is a measurement, not an artifact. Where a run's data earns keeping (a calibration record for the instrument itself), it lives in `evals/`, the way the sibling reader-position and panel-gate records do.
