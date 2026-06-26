---
name: premise
description: >
  Author a Premise (the Assignment whose ends are still open, a grounded
  opinion stated plainly enough that a reader could find it false) into the
  tracker, in this thread. Carries the discrimination gate for all four
  Assignment kinds: it authors a Premise, sends a settled-ends goal to
  /direction, and bounces an operator-originated Command or Manual to the
  operator's own verbs. Pass --spawn to also spawn a Bob on the filed Premise.
---

# Premise

A **Premise** is the Assignment whose *ends* are open: a grounded opinion about the system, stated plainly enough that a reader could find it false against the code. `/premise` writes one into the tracker from the conversation you are in, for a Bob who will pick it up without that conversation. Author for that Bob: what does it need in order to do the right thing?

`/premise` is also the default door into authoring, so the discrimination that sorts the four Assignment kinds lives here. Run it before you compose.

## Which Assignment is this?

Four kinds come through this door, and the door's first job is to make sure the one you are holding is the kind you compose. The authoring gate checks only that each kind carries a Route its kind allows; it never checks that you picked the right kind. A Premise and a Direction are stored alike but for a type label, and a mislabel is caught by nothing downstream. You are the only guard.

One question sorts all four: **where does discretion over this work lie?** It is not a label to match against examples; it is what every kind is an answer to, and it resolves in two cuts taken in order. First, *whose* discretion: did you reason your own way to this, or are you only recording a call the operator has already settled? Second, for the work that is yours, *how open* the goal still is: arguable, or settled? Reason from that question and a case the rule never names still comes out right; reach instead for the surface shape of the work (how big, how open-ended, whether it sounds like an order) and the look-alikes across the kinds will cross you up.

Before either cut, one threshold. **Is there a claim here at all?** A description of how something behaves (*the spawn path leaks worktrees*) asserts nothing a peer can argue with until you say what you would do about it and would defend that. Do not file a bare observation as a Premise; rewording it to sound like an opinion does not make it one. Find the real position under it and author that; or, if you will not work it out now, capture it with `/tangent` rather than inventing a position you do not yet hold. When the observation is your *own failure*, the position under it (the belief it overturned, or, when no belief of yours could have averted it, the preventable defect in the scaffold it exposed) is what `/postmortem` recovers and files.

**First cut: whose discretion is this?** You author the kinds you reason your own way to, a Premise or a Direction; you never originate the kinds whose authority is the operator's, a Command or a Manual. The line is what the operator *settled*, not what they raised: an operator who points at a goal but leaves you to work out what to build or how has handed you reasoning to do, and the call is yours. So when you are only the scribe for the operator's call (settled work to carry out, or a standing situation you can state only as what the operator will direct live) you do not originate it here: a directive to execute is a `/command`, the operator keeping the wheel and feeding intent turn by turn is a `/manual`, and each is the operator's to invoke, so nothing files under their authority that they did not give. When you genuinely cannot tell whether the operator settled it, do not resolve the doubt by authoring a Premise; bounce it to the operator, the way a clear Command or Manual is bounced to their own verbs. The errors are not equal, and not the way they first look. Author a Premise on what was the operator's settled call and it is pickable the instant it is filed: it enters autonomous pickup without the sign-off readback that holds a Command or Manual outside the pool, the very protection this cut exists to guard, and nothing downstream catches the bypass. Bounce what was actually yours and the cost is only a round-trip: the operator hands it back as yours, you author the Premise a turn later, and nothing was invented, because you could not have filed under their authority regardless: only the operator originates a Command or Manual. The silent default is the dangerous one, so when the doubt is whether the call is the operator's, make the operator the one to settle it.

**Second cut: how open is the goal?** This runs only on the work that is yours, and it sorts a Premise from a Direction. Default to a Premise and make settledness carry the burden of proof, because here too the errors are not symmetric: file a Direction as a Premise and you waste an argument the reader re-runs; file a Premise as a Direction and you have quietly declared a live goal closed, and the cross-examination that should have happened never does.

- **Is there any live reason left to contest the goal itself?** If you can name even one, it is a Premise: the ends are still open, whatever else is decided.
- **A Direction earns its kind only when the ends are settled on exactly one assumption you can name (the hinge) whose failure would reopen the whole call.** If it takes more than one, or you cannot crisply name the one, the ends are not settled and you hold a Premise. The single hinge is not a hoop to clear; being unable to find it *is* the signal.

When you settle on a Direction, author it with `/direction`, whose body is built around that hinge. Everything below is the Premise path.

A Premise takes one of three shapes, chosen as its Route when you compose, but worth knowing now, because two of them are where work that does not look like an ordinary Premise belongs. A **check-in** Premise is the common one: a worked proposition the reader reaches through a bounded conversation. A **plan** Premise has a goal too large for one Assignment; its deliverable is the set of children it decomposes into, and its work is `/decompose`. An **explore** Premise is open-ended: a starting point for a conversation with no fixed deliverable. Hold the explore shape against the Manual. The two look alike, both running live and unbounded, and only the first cut tells them apart: an explore Premise is open-ended work *you* reasoned into, a Manual is the operator holding the wheel. If the open-endedness is yours, it is an explore Premise, not a Manual.

## Write so the reader can fight it

The reader is a peer with more current information than you, the operator within reach, and the code to check you against: everything except this conversation. Carry the slice of it they need, in the humble-snapshot shape doctrine sets out; read [[premise-frame]] for that shape and do not paraphrase it here.

Beyond the frame, author for one thing in particular: the reader should feel free to scrutinize the proposition itself (whether this is worth doing at all) not merely whether your framing survives the code. A Premise the reader can only agree with has failed before it was picked up.

## Compose, then file

**Title first: the proposition as a phrase.** What you believe, with the *how* and the *whether* left to the reader. The constraint is a forcing function: a claim you cannot reduce to a phrase is a claim you have not finished thinking, so stay here until it reduces. A title in the imperative (*fix X*) or pitched as its own negation (*X shouldn't happen*) is the tell that you are still holding a task; restate it as what you believe to be true. The scope that carries the boundary (phase markers, qualifiers) rides in the title, so the reader inherits the boundary you drew rather than a silently widened one.

**Then the rest:** the body in the frame above; the **Component** prefix the work belongs under (`PM`, `CORE`, …, which need not be the cwd's); the **Route** (the Premise shape the gate named, `check-in` if unsure, its only cost a conversation that was not strictly needed); and any **Depend** edges on already-resolved prerequisites.

**One Component, but not one repository.** The Component names where the Premise's *substantive* work belongs; it does not cap the Premise at a single repository. When that work forces a consequent mechanical change in a peer (a contract following the change that drove it) the peer change belongs to *this* Premise as a second coordinated PR, not a Premise of its own; splitting them ships an incoherent state until both merge. Split only when the peer change is itself substantive. The Component entry in `~/.vaudeville/doctrine/vocabulary.md` is the authority.

**Then read it twice before filing: the corruption read.** A single-use body earns one light pass against the moves that corrupt the reader downstream, and stops there. Once as yourself: did you slip into a project manager's register, scope decreed, doneness defined, mechanism dictated, acceptance criteria smuggled in? Once from the seat of the Bob who will implement it: is there a dogwhistle that would make a capable peer hear an order where you meant a proposition? Cut whatever either read turns up. (`/direction`, `/command`, and `/manual` run their own tuned versions of this same read.)

File through single-quoted heredocs, so backticks and other shell metacharacters in the body stay literal rather than running:

```bash
summary=$(cat <<'PREMISE_SUMMARY'
<the proposition, as a phrase>
PREMISE_SUMMARY
)
description=$(cat <<'PREMISE_BODY'
<the humble-snapshot body>
PREMISE_BODY
)
new_id=$(vv file --project <PREFIX> --summary "$summary" --description "$description" --route <ROUTE> [--dep <PEER>...])
```

Each closing delimiter sits at column 1, or the heredoc will not close. `vv file` is the kind-agnostic authoring primitive (it defaults to Type Premise) and prints the new Premise's id.

If the operator passed `--spawn`, put a Bob on it; otherwise it waits in the pickup pool for a later `/spawn`:

```bash
vv spawn "$new_id"
```

`vv spawn` cuts the worktree and seeds the Bob, which claims the Premise on its own first turn; you do not claim it yourself. Report one line: the new id and its Route, plus the `wm open` target `vv spawn` printed if you spawned.
