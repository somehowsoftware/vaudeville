---
name: prose
model: opus
effort: max
description: >
  Compose one coherent piece of agent-facing prose for one reader-situation:
  ground the premises it rests on against their source, settle the framing with
  `/frame`, draft, purge from the reader's chair, check every line against what
  the reader holds, fill the gaps, and test the result by its effect with
  `/assay`, redrafting until it carries force. When the prose in front of you
  spans several reader-situations, the partition is your first judgment: cut by
  reader, and run this composer once per piece. Stops at a finished piece; it
  does not deliver.
---

# Prose

Compose one coherent piece of agent-facing prose, addressed to one reader-situation. When the prose in front of you spans several reader-situations, the partition is your first judgment, made before any composing: cut it into pieces that each share a reader, a purpose, and a frame, so that a single framing and a single assay serve each. The cut is by reader, not by file — two files that are one argument to one reader are one piece; one file addressing two genuinely different readers can be two — and often the answer is one piece; let the count follow the work, never a shape imposed on it. Run this composer once per piece. From here down you hold exactly one piece and one reader.

Agent-facing prose is nondeterministic code: another agent acts on the words you wrote, with nothing to go on but those words and what it can observe. It is a force, not information: the reader does something differently because the words pulled it, or the words did nothing. The fewer the words, the more weight each one carries, so the most powerful agent-facing prose is plain, clear, and brief.

Agents treat ordinary code with care and treat agent-facing prose as an afterthought. The training corpus treats it as glue, and the pull is to dash it off. This skill exists to resist that pull and make you grapple with the seriousness of the charge.

## Neither length nor profile is a proxy for impact

The size of a change is no measure of its weight. If you are here to edit a single phrase, it is because that phrase mattered enough to spend a whole session on: a reason to treat it as heavy, not light.

This holds even though a lighter pass exists elsewhere. An Assignment body earns one at authoring time, but earns it from its reader's correction loop, the picker pressing it against the live code as the authoritative tiebreaker, not from being small; the prose this composes has no such reader. The relief is the reader's, never the prose's profile. See `~/.vaudeville/doctrine/practice/signal-side-leverage.md`.

## This process is not a replacement for responsibility

Read this skill through before you act. If any of it is ill-suited to your task, stop and raise that with the operator rather than bending the prose to fit. "This seems minor" reads as fluency when it is in fact ignorance.

## Agent-facing prose balances two competing goals

Agent-facing prose is read two ways. An agent reading a skill executes it under its own discretion; an agent reading exposition acts to extend what it understood. Both readings face the same pull in opposite directions: too thin, and the reader drifts from its purpose; too constrained, and you crush the judgment you reached for agency to get.

Vaudeville does not shackle the reader, because shackles crush resilience. It relies on clarity of purpose: a reader that holds *why* it is acting stays on course without fences, and adapts when the situation departs from anything you foresaw. Your reader is as capable as you, and it holds information you do not. Inform it; do not command it.

The exception is the line whose crossing cannot be undone: the irreversible or externally-visible act, where no judgment the reader brings makes a wrong call recoverable. There, state the rule flat. Name its reason even so, so the reader holds the line at the next case you did not list.

# Procedure

## 1. Review the doctrine

Re-read from source the doctrine that governs these words before you write; a warm context hands it to you as fluent memory, which is not the same as having it open in front of you:

- `~/.vaudeville/doctrine/code/language.md`: naming and comment discipline.
- `~/.vaudeville/doctrine/code/intent.md`: the WHAT/HOW/why layering.
- `~/.vaudeville/doctrine/bearing/davar-chadash.md`: the reader is frontier-capable; prose that pre-chews produces worse output, not safer.

## 2. Scope the outcome

Work out how the prose will be used, and sit in the chair of the agent who will read it. What does the best outcome look like? How could it go wrong? What would let it stay resilient in a situation you never foresaw, and what would make it retreat into checking boxes and quoting aphorisms? This is the reader-situation the rest of the procedure composes for.

## 3. Scrutinize the interaction space

You would not edit a function without reading its call sites, dependencies, and tests; treating prose as an isolated edit is the same negligence. Preserving the reader's judgment gives almost every change a wide blast radius. Read everything that depends on, or sets the context for, the text you are touching. Potentially all of it needs to move. Ask what must stay true, what will no longer be true, what is already misleading, and what nearby text would make your readers more effective if you cleaned it up while you are here.

## 4. Ground the premises against their source

Everything else in this procedure tests how well you encode what you mean; none of it tests whether what you mean is true. The cuts you will make, the line-by-line check that each line resolves for the reader, the force-test at the end: each works inside your premises, taking what the prose asserts about the world as given and asking only whether you encoded it well. A premise you hold confidently and wrongly passes all of them untouched, and the force the rest of this procedure builds does not expose the error but amplifies it: a reader trusts forceful, well-made prose more, not less, and acts on the falsehood holding nothing but your words. The force-test looks like it should catch this, but a fresh reader inherits your premise along with your prose and converges on the same wrong act, which reads as force, not error. You are the last point from which a false premise is touchable from outside it. So ground the premises before you build on them.

You cannot do this by looking harder at your own conviction. The premise that sinks you is not one you would list if asked for your assumptions; that one is already a candidate for doubt. It is the one that has become the floor you stand on to write; you hold it as how the world is, not as a claim you are making, so "am I sure?" returns yes every time. Your confidence is not evidence; it is the faculty that already failed. What corrects you is contact with something outside your head that can answer back and say no. So do not interrogate yourself. Go to the source.

For each claim your prose leans on:

- **Find the ones that bear load.** A claim bears load when, were it false, your prose would steer the reader wrong: you would have to tell it to do something different. Judge by that, not by how weighty or how certain the claim feels; the dangerous claims are often the ones you are surest of. When you cannot tell whether a claim bears load, treat it as if it does. This is the same set the rest of the procedure already turns on: every line that changes what the reader does rests on a claim about the world.
- **Say what would show it false.** State the claim as a flat assertion you could be wrong about ("the kernel clears the working tree before it writes," not a sense that it does), and name the observation that would prove it false. Naming the falsifier first is what lets the answer correct you instead of being read as agreement; a claim with no falsifier is a conviction, and a conviction cannot be grounded.
- **Go to where its truth lives, not to the nearest copy of it.** Each such claim is true or false somewhere outside you: in another repository, a running system, a contract another context owns, what the reader actually holds. Reach that authority and let it answer; do not reach the copy in front of you, which agrees by construction because it is where your belief came from. The sharpest case, and the one to carry: a claim about another repository's code is true or false at that repository's current state on the network: `origin/main`, not the clone on your disk, which drifts the moment you look away. Checking what is in front of you compares your belief against another copy of your belief, and passes every time. Read the live remote.

None of this is a checklist of claim-kinds to clear: repository claims, contracts, conventions. A list teaches you where it ends, and the premise that ships wrong is the one just past the edge of whatever list you drew; the move is the same whatever the claim is about. When grounding turns up a premise that was false, you have learned the prose would have been wrong before you spent its force making the error persuasive: change what you believe, then compose.

## 5. Settle the framing

Invoke [`/frame`](../frame/SKILL.md) via the Skill tool: bring it the reader and what the prose must achieve, let it consult the right panel from outside your frame, and commit to an approach before you draft. The framing is the angle this piece takes toward its reader; the drafting below is written to it.

That decision is yours to carry, not to clear. The panel's whole job was to diverge from your plan; that it did is the panel working, not a signal to stop. Record the divergence and how you resolved it where the piece is reviewed — for repository work, the pull request that tenders it — that record is how you surface it, and that review is where the operator weighs what you chose. If what you are about to do could be discharged by stopping and asking the operator, you have mistaken visibility for permission.

Carry the divergence there unless the review can no longer set it right: the change would reach outside that review and cannot be taken back, or it overturns the goal the operator committed to, so review would be anchored to a goal they never chose. Those, return to the operator now; everything else you carry. When unsure, carry: a divergence carried wrongly is caught at review, while one bounced wrongly spends the attention the operator cannot spare.

## 6. Author a maximalist draft

Get it all out. This is not the place for parsimony: write the expansive version, since the cutting comes next. When the framing left several angles live and you cannot yet tell which works, draft them in parallel (subagents, or `claude -p --resume <id> --fork-session`, so they do not clobber each other) and reconcile into one.

When your source for the prose is itself an enumerated list (a Digest discussion, a prior draft, a sweep of edits), do not transcribe it into prose. That list was written from your position, not the reader's, so transcribing it carries your blind spots straight onto the page. Re-derive the prose from the reader's why; treat the list as a fallible sketch of what to cover, not the words to ship.

## 7. Purge: three passes, default cut

Go through the draft three times, at three granularities: each paragraph; then each sentence of each paragraph; then each clause of each sentence. Run all three: the coarse pass cuts whole moves the fine passes never reach, the clause pass catches dead weight a paragraph reads straight past.

For this pass, stop being the author and be the reader about to act on these words, holding only the prose and what it can observe. The author cannot run it: from the author's seat the labor that earned each line is still lit, so every line reads as earned and the draft already looks tight. From the reader's seat the question is never whether a unit helps. Almost every true line helps a little, which is why "does it help?" keeps everything and the draft never thins. The question is whether the reader would act worse without it.

So invert the burden. Every unit starts cut, and earns its place back only if you can name the specific worse thing the reader does without it: a wrong turn, a mishandled case, an omitted step. That a line is true, well-put, or hard-won does not earn it; only a named failure in the reader's action does. The bulk this removes is the prose that served you in reaching the point: the working-out, the justification, the throat-clearing toward a thought. You needed the road to reach the point; the reader needs the point, and rebuilds the road from it.

Cut hard, because the gap-fill pass that follows re-adds what the reader turns out to need. But that net catches only the loud miss: cut a step the reader cannot proceed without and it stalls in plain sight, the gap shows, the next pass restores it. The net never catches the silent miss. Cut the reason behind a non-obvious rule, or the guardrail against a rare but unrecoverable case, and the reader proceeds confident, acts the same in every ordinary case, and goes wrong only at the one case whose warning you cut, with nothing to mark the loss. So weight a unit by the cost of the case it governs, not by how often that case arrives: toward the loud, recoverable miss cut freely; toward the silent one, never. A line whose absence the reader would not notice but could not survive stays.

What no criterion hands you is which line that is: whether this clause is load-bearing for an act you cannot foresee. That read is yours, made from the reader's seat at the margin where it would go wrong.

## 8. Check every line against what the reader holds

The purge cut what the reader does not need. This pass catches what it cannot use: a line whose meaning lives in your context and not in the reader's, so the reader has nothing to act on. You cannot find these by imagining the reader, because the reader you imagine is yourself with everything you know still lit; you cannot see an absence you are still supplying. So do not judge it. Test it.

Write down where the reader stands when it reaches this prose: what it holds (its Foundation, and the words of this prose up to this line) and what it has not reached (a later phase of its work, any earlier draft of this prose, anything about its task you have not put on the page). Then walk the draft for every place it points at something outside itself, and for each, find what it points at in what the reader holds, or change the line:

- **A prohibition against a wording the reader never saw.** "Do <correct thing>, not <already-deleted instruction>" forbids a phrasing whose only source is a draft the reader never read: the warning is the reader's first sight of the very words it forbids, so it hands over the thing it meant to prevent. State the destination you want; never the distance from a place the reader never stood. This is the pointer no reader and no later check can catch for you, because the fact that resolves it, that you are reacting to your own earlier draft, is one only you hold; run this pass hardest. Heading off a move the reader could make on its own is a different thing and is fine: "don't write a plan", "make no edits yet" correct a default the reader already holds and can act on. The phantom is only the wording the warning itself introduces.
- **An instruction, or a tell to watch for, that belongs to a later phase.** A reviewer's behavior, rounds of review, a draft you have already written, a first failure, a CI result: each is a sign from a phase the reader has not reached, even while it works hard in an earlier one. If the reader cannot be standing where the sign appears, it is premature; keep the insight at the reader's altitude, or move it to the turn where the reader will stand.
- **A definite reference, or a claim about the content you did not write.** "Surface that one question" or "the author named a hinge for you" point at something the surrounding content was meant to supply. If nothing the reader holds supplied it, the reader must invent your meaning to comply. The trap hides at the seam where fixed framing meets interpolated work-item content: framing that asserts a fact about that content ("a question is still open", "the author named X") is a phantom referent wherever the content does not bear it out. Hold the framing against the range of content it will wrap, not the one example in your head; supply the referent or drop the claim.

A pointer whose referent the reader does hold is not a defect, and flagging it is its own failure: an author buried in false flags pads the prose to clear them, which is the disease. A term the reader's Foundation carries, or one this prose introduced before the pointer, has its referent; leave it. The test is whether this reader holds the referent, not whether the word appears twice in your draft.

This pass can talk itself past a premature pointer, so back it with a fresh reader. Spawn a Foundation-primed agent that reads the draft as the reader at its exact lifecycle moment and reports any line it cannot act on from where it stands; it reliably catches the premature pointer this pass rationalized away. It cannot catch a phantom, because no reader can: that one stays with you, who alone holds the earlier draft the phantom warning reacts to. The detector and its calibration live in `evals/reader-position/`.

## 9. Fill the gaps

The purge only removes. Now ask the opposite: what does the reader still need that is not on the page: a step assumed, a failure mode unnamed, a move told without telling how? The gaps hide in what goes without saying to you; that is exactly what the reader was missing. Add that, and only that.

## 10. Test the result by its effect

Invoke [`/assay`](../assay/SKILL.md) via the Skill tool: hand it the finished piece and the reader it is for, and let it measure whether the prose moves what a reader does. The assay returns a verdict, not a decision (load-bearing, misfiring, or inert), and the decision is yours, because you hold the work it does not.

- **Inert** is the verdict to expect and the one to act on: the prose changed nothing a capable reader would not already do. Cut the dead weight, or find the case the prose should decide and sharpen it there, then assay again.
- **Misfiring** sends you back to the framing: the approach, not just the wording, moved the reader wrong.
- **Load-bearing** is done.

The assay tests force, not correctness, and it is blind to the author-side defects steps 4 and 8 exist to catch: a false premise moves the reader with full force and a phantom moves no reader, so the assay reads the first as load-bearing and the second as inert, neither as the defect it is. These passes are complementary, not redundant; none stands in for the others.

## 11. Make the coupled non-prose edits

A prose change is often coupled to a small non-prose edit (a config file, a registry entry, a line of code) that makes it real. Make those, so the prose and the wiring that activates it are ready together. If they run substantially out of scope, stop and ask the operator.

## 12. Question the outcome

Survey the whole. Could it be called superficial? Will the agentic review catch a defect you should have caught first? The protocol does not discharge your responsibility: do whatever else it takes to leave your reader able to do what it was sent to do. Then stop: this composer ends at a finished piece. Delivery belongs to the goal the piece serves: when every piece the work needs is composed, carry the finished work onward — for repository work, `/tender` takes it to its pull request.

## On failure

The rare divergence you do not carry is the one that leaves you no version you can stand behind — not unsure which of two workable versions to ship, which you carry, but none you would put your name to, because the framing splits on the core and your hardest read cannot land one, or the prose wants a flow no cast can sharpen. Stop and return it to the operator rather than composing past it. A divergence that settles on a version you can stand behind, however far it moved you off your plan, is not this case; resolve it and carry it.
