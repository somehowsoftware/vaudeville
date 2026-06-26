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

## Confirm you hold a Direction, not a Premise

`/premise`'s gate sorts the four kinds in two cuts: whose call this is, then how open the goal is. Its first cut already settled that the call is yours, not the operator's. The second cut is the Premise/Direction line (the one nothing downstream catches), so re-run it here, even if you reached `/direction` directly:

- **Name the hinge: exactly one assumption, whose failure reopens the goal.** If it takes more than one, or you cannot crisply name the one, the ends are not settled. That is a Premise; go to `/premise`.
- **Is there a live reason left to contest the goal itself, beyond the hinge?** If so, the ends are still open: a Premise, not a Direction.

The bias is toward Premise: a goal you have called too early, dressed as a Direction, forecloses an argument that should have happened, and no machinery will notice. When unsure, author a Premise.

## Compose the body

A Direction's body has four parts, and they are the kind's whole shape:

- **The call.** What you have decided, as a claim: the settled goal, stated so the reader inherits it cleanly.
- **Why it was made.** The reasoning that closed the ends. The reader adapts the means to reality only if they hold the why; without it they execute the letter and miss the point.
- **The hinge.** The one assumption the call rests on, named so it can be *attacked*. The hinge is not acceptance criteria: not a condition to satisfy but the single thing whose failure reopens the call. If you find yourself writing a list of conditions the work must meet, you have drifted back into acceptance criteria; cut back to the one assumption that actually carries the goal.
- **What the call becomes if the hinge gives.** Where the reader arrives if they attack the hinge and it breaks: the call reopens to *what*. This is what tells the reader the hinge is live, not decoration.

Lead with the call; the means are the reader's. Stating the steps the reader should take settles what a Direction deliberately leaves open; if you cannot help dictating the how, the ends were not the only thing you had decided, and this may be a Command.

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
