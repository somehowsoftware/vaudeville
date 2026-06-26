---
name: postmortem
description: >
  Turn a failure you just had into a Premise a future peer can act on. The
  title is the lesson under the failure (the belief you held that it proved
  wrong, or, when no belief of yours could have averted it, the preventable
  defect in the scaffold it exposed), not a report of what broke or an
  instruction to fix it; the incident is demoted to context. Files an ordinary
  Premise with a provenance banner so postmortems can be found and counted.
  Pass --spawn to spawn a Bob on it.
---

# Postmortem

You failed (shipped wrong work, misread a core concept, drifted off the task) and the lesson in it is worth more than the fix. `/postmortem` turns that failure into a **Premise**: a proposition a future peer picks up without your conversation, and either acts on or argues with. The skill is the conversion the operator otherwise does by hand: from *what went wrong* to the contestable proposition underneath it, usually a belief you held, sometimes a defect in the scaffold you ran.

A postmortem is an ordinary Premise: no new Assignment kind, no special Route; postmortem-ness lives in this skill and a banner, not the type system. Everything `/premise` knows about authoring a Premise holds here. This skill adds only the conversion and the banner.

## When this is the skill

A failure worth a postmortem leaves a lesson a peer could not reach without the conversation you are about to lose. One question sorts which kind you have: *could a competent peer in your seat, holding a different belief, have avoided this?* The operator may point you at the failure; you may also catch your own.

**When yes, the belief you held is the lesson**: the thing a competent version of you would have asserted going in that the failure falsified. Recovering it is the first branch below. Take it even when the scaffold also misbehaved: the part you could have held differently is the part worth teaching, and it is the harder thing to face. When that misbehavior is itself a preventable defect (one a peer who did not share your wrong belief would still have hit) it is a second lesson with its own home; file both, the belief for your seat and the defect for the scaffold. What you may not do is let the defect stand in for the belief you would rather not face.

**When no (a competent peer in your seat fails exactly as you did) your belief was not the problem.** That is not yet silence. If the scaffold you ran broke in a way it could have prevented (a skill's steps, a command, a hook, a composition step) and no belief you could have held would have routed around it, the failure still warrants a postmortem, because the defect still needs fixing. That is the second branch.

It is still not every failure. A typo, a flaky test, a slip where you already knew better: these broke something, exposed no belief, and expose no preventable defect; there is nothing to contest and nothing to file. Say so and stop. When you are unsure either branch is real, file anyway and let the check-in test it: an unfiled lesson is gone for good, a thin one is cheap to close.

## The conversion: recover the belief, then try to break it

This is the part that is easy to fake and the part that matters. The failure sits in front of you, already resolved, and the pull is to write down what you now know. Resist it. The lesson is not the correction; it is the **wrong belief you were running** the instant before you acted: the one you would have defended out loud had someone stopped you. Recover that, and write it in the present tense, as a claim, as if you still held it.

Two moves get you there:

1. **Recover the belief.** Ask: *what did I take to be true that this failure shows a capable peer should not assume?* Not what broke: that is the incident. Not what to do: that is the fix. The assumption the work rested on. You may have to build the sentence rather than find it sitting there; the belief was operating silently, which is why it cost you.

2. **Try to break it.** Write the negation of your title. Keep the title only if both hold: a competent peer *could have held that negation* (it is a live position, not an absurdity nobody defends) and *believing the negation in advance would have changed what you did*. If no one would ever assert the negation, your title is a platitude. If believing the opposite would have changed nothing, your title still points at the crash, not the assumption that steered into it. Either way, return to move 1.

A real lesson names a choice a peer would make differently; a fake one fills the slot with something true and inert. The title has to be a belief with a stake: someone could hold it, someone could deny it, and which they hold changes what they do.

A worked example, kept far from your own situation so you take the shape, not the subject. An agent deletes a database column it judges unused; a nightly job that read it breaks.

- *The incident, told straight:* "Dropping `legacy_id` broke the nightly reconciliation." True, and useless to a peer.
- *A fix in declarative clothing:* "Columns should not be dropped without checking downstream readers." Contestable only in grammar; its negation is something no one defends. A platitude.
- *The belief, recovered:* "A column with no references in the application code is unused." That is what the agent held, and it is wrong: schema-level and out-of-band readers exist that the code never names. A peer could hold it, could deny it, and believing its negation in advance would have stopped the deletion. That is the title.

## When the scaffold failed, not your belief

Sometimes the recover-and-falsify test comes up empty for the honest reason: no belief you could have held would have changed the outcome, and a competent peer in your seat fails exactly as you did. The lesson has not vanished; it has moved, from a belief in your head to an assumption built into the scaffold that the failure just falsified.

Recover that assumption. Ask: *what did the scaffold take for granted that this failure shows is false?* The composition step that assumed the body held no single quotes; the spawn that assumed a repository's `origin` is always populated; the hook that assumed its event fires once and never twice. Name it as a contestable diagnosis (what the scaffold did, and why that is a preventable defect) in the present tense, so a peer can fight it: deny the defect is real, deny it was preventable, or hold that the behavior is relied upon somewhere you did not look. A remedy, if you see one, rides as a contestable lean, never a fix to carry out; you hand over a diagnosis, not a work order.

The honesty gate from the belief branch applies here, pointed the other way. You reach this branch only by having run the belief test and found it genuinely empty. So write, in the body, the competent peer who would have failed exactly as you did. If you cannot write that peer, a belief you could have held would have saved you, and this is that belief's postmortem blamed on the scaffold to avoid facing it: go back to the first branch. The scaffold is the easier thing to blame, which is the whole reason the belief test runs first.

## The body: the lesson leads, the incident follows

Compose the body in the humble-snapshot shape every Premise takes. [[premise-frame]] has it; do not paraphrase it here. The one difference is that the incident, which a person would make the whole writeup, is demoted to a section of situational context: lead with the lesson (the belief you now doubt, or the defect you now name) and why, then recount what happened as the evidence that surfaced it. A remedy, if you have one, rides as a contestable lean the reader may reject: never acceptance criteria, never a fix to carry out. You hand over a corrected understanding, not orders.

Read it back once before filing: did the title slide into the incident or the fix while you wrote the body? The body's detail pulls it there. Cut it back to the lesson.

## File it

Stamp the provenance banner verbatim at the top of the body; it marks the Premise a postmortem for its reader and makes postmortems findable and countable, as `/tangent`'s banner marks a provisional capture. Two banners follow; stamp the one that fits the branch you took, verbatim, as the body's first line.

For a belief postmortem:

> **Postmortem.** This Premise is a postmortem: its title is the belief, held going in, that the failure below exposed as wrong, a contestable lesson, not a report of what broke or a fix to carry out. Fight the proposition itself; the incident is situational context, not a verdict.

For a scaffold postmortem:

> **Postmortem.** This Premise is a postmortem: its title is a preventable defect in the scaffold that the failure below exposed (one no belief in the failing seat could have averted), a contestable diagnosis, not a report of what broke or a fix to carry out. Fight the proposition itself; the incident is situational context, not a verdict.

File through single-quoted heredocs so backticks and other shell metacharacters in the body stay literal:

```bash
summary=$(cat <<'POSTMORTEM_SUMMARY'
<the lesson, as a phrase>
POSTMORTEM_SUMMARY
)
description=$(cat <<'POSTMORTEM_BODY'
<the banner that fits your branch, verbatim>

<the humble-snapshot body, incident demoted to a "what happened" section>
POSTMORTEM_BODY
)
new_id=$(vv file --project <PREFIX> --type Premise --route <ROUTE> --summary "$summary" --description "$description" [--dep <PEER>...])
```

Each closing delimiter sits at column 1, or the heredoc will not close. `vv file` is the kind-agnostic authoring primitive; `--type Premise` files the kind and the banner does the marking, so no core change and no new Route are needed.

- **Project.** File where the discipline the lesson would change lives, often not the repository you were working in. A lesson about the prose-process belongs to the context that owns the prose-process; a defect in a spawn skill, to the context that owns it. Name the home of the thing the lesson is about.
- **Route.** `check-in` by default: a postmortem is a proposition inviting contest, and the check-in is where a peer pushes back. Choose `explore` when the failure opens a question too wide to settle in one conversation.
- **Spawn.** If the operator passed `--spawn`, put a Bob on it; otherwise it waits in the pickup pool for later triage:

```bash
vv spawn "$new_id"
```

## Report

One line: the new Premise's id and Route, that it was filed as a postmortem, and (if you spawned) the `wm open` target `vv spawn` printed.

If you have not worked the failure out at all and only want it off your plate, that is `/tangent`, not this; a postmortem is composed, the thinking already done.
