---
name: direction
description: >
  Author a Direction (the Assignment whose ends are settled on one named
  assumption, the hinge, while the means stay open) into the tracker, in
  this thread. The kind a decomposed plan's settled leaves usually take.
  Route check-in. Pass --spawn to also spawn a Bob on the filed Direction.
---

# Direction

A **Direction** is the Assignment whose *ends* are settled (but settled on a single named assumption, the **hinge**) while the *means* stay open. You have made the call; you are handing the reader the goal and leaving the how to them. The hinge is the one assumption whose failure would reopen the whole call, named so the reader knows exactly where to push. Naming it is what makes a Direction *easier* to argue with than a Premise marked merely provisional, not harder.

## Is this an Assignment at all?

Before sorting which kind, check that the work stands alone. A small change whose content is already settled by work in flight — the contract, names, or strings it would carry live in a sibling Assignment's conversation and PRs — is not a Direction; it is a piece of that work, and it ships as a coordinated PR on the driving Assignment, now. Filing it separately forces you to transcribe the settled details across an Assignment boundary, and transcription is where they corrupt: the reader receives a decree, severed from the conversation that settled it, and presses nothing. The tell in the wild is a body managing the incoherent state the split itself created — a merge-ordering note between "coordinated halves" is the split confessing.

When nothing is in flight for it to ride, a settled-and-small change is still not worth a hand-off: suggest doing it now, with the operator recording it afterward as a backfill Command marked delivered — the operator's verb and the operator's call, and the tracker residue survives without a hand-off nothing needed.

Either way this is a suggestion you surface, not a refusal: name the off-ramp, and file the Direction if the operator confirms the work should stand alone.

## Confirm you hold a Direction, not a Premise

`/premise`'s gate sorts the four kinds in two cuts: whose call this is, then how open the goal is. Its first cut already settled that the call is yours, not the operator's. The second cut is the Premise/Direction line (the one nothing downstream catches), so re-run it here, even if you reached `/direction` directly:

- **Name the hinge: exactly one assumption, whose failure reopens the goal.** If it takes more than one, or you cannot crisply name the one, the ends are not settled. That is a Premise; go to `/premise`.
- **Is there a live reason left to contest the goal itself, beyond the hinge?** If so, the ends are still open: a Premise, not a Direction.

Then read your draft once for dictated means — contract details, mechanisms, file paths, steps — and ask of each where it came from. Three sources, three different findings:

- **Transcribed from work in flight.** The detail already lives in a sibling Assignment's conversation; you are copying it across a boundary. That is the coordinated-PR case above, whatever the hinge looks like.
- **Invented here to close the goal.** A call the reader's own conversation should make, decreed so the ends would feel settled. Ends that need propping are not settled: author a Premise, and let the proposition carry what you actually hold.
- **Neither — the call stands without them.** Then they are backseat driving: cut them and file the lean Direction, because a truly settled call states clearly with the means left wholly open. (Means the *operator* settled and handed you are none of the three: that is a Command, the operator's verb; bounce it there.)

This screen runs on that named evidence, never on size or felt import: a large call, cleanly stated on one hinge, is a Direction. The bias stays toward Premise: a goal called too early, dressed as a Direction, forecloses an argument that should have happened, and no machinery will notice. When unsure, author a Premise.

**Arrived from a `/decompose` round?** A leaf minted from a blessed round inherits its settledness from the round — the plan conversation already adjudicated the goal — so do not re-run this screen to demote a settled leaf; a leaf is a Premise only when its own ends are open, `/decompose`'s own rule. The threshold question above still applies inside a decomposition: a candidate too coupled to a sibling is the pressure-test's merge case.

## Compose the body

A Direction's body has four parts, and they are the kind's whole shape:

- **The call.** What you have decided, as a claim: the settled goal, stated so the reader inherits it cleanly.
- **Why it was made.** The reasoning that closed the ends. The reader adapts the means to reality only if they hold the why; without it they execute the letter and miss the point.
- **The hinge.** The one assumption the call rests on, named so it can be *attacked*. The hinge is not acceptance criteria: not a condition to satisfy but the single thing whose failure reopens the call. If you find yourself writing a list of conditions the work must meet, you have drifted back into acceptance criteria; cut back to the one assumption that actually carries the goal.
- **What the call becomes if the hinge gives.** Where the reader arrives if they attack the hinge and it breaks: the call reopens to *what*. This is what tells the reader the hinge is live, not decoration.

Lead with the call; the means are the reader's. Stating the steps the reader should take settles what a Direction deliberately leaves open; when means keep creeping into the draft, run the three-source read from the gate above rather than shipping them — a settled call states cleanly without them.

**Read it once before filing: the corruption read.** The same light single-use pass `/premise` runs, plus one tuned for this kind: did the hinge harden into a checklist? Did you slip into a project manager's register, scope decreed, doneness defined, means dictated? Cut what the read turns up.

## File it

A Direction's only Route is check-in: the means are open, so the work wants a conversation; the ends are settled, so that conversation does not re-litigate the goal. File through single-quoted heredocs so shell metacharacters in the body stay literal:

```bash
summary=$(cat <<'DIRECTION_SUMMARY'
<the call, as a phrase>
DIRECTION_SUMMARY
)
description=$(cat <<'DIRECTION_BODY'
<the call, why, the hinge, what the call becomes if the hinge gives>
DIRECTION_BODY
)
new_id=$(vv file --project <PREFIX> --type Direction --route check-in --summary "$summary" --description "$description" [--dep <PEER>...])
```

Each closing delimiter sits at column 1, or the heredoc will not close. `vv file` is the kind-agnostic authoring primitive; `--type Direction` files the kind, and a Direction is admitted only on check-in, so any other Route is refused at the gate. `vv file` prints the new Direction's id.

If the operator passed `--spawn`, put a Bob on it; a Direction is spawnable like a Premise, and its picker reads the call, presses the hinge, and realizes the means:

```bash
vv spawn "$new_id"
```

`vv spawn` cuts the worktree and seeds the Bob, which claims on its own first turn. Without `--spawn`, the Direction waits for a later `/spawn`. Report one line: the new id and its Route, plus the `wm open` target if you spawned.
