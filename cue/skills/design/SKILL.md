---
name: design
model: opus
description: >
  Run a design pass after the goal is agreed and before implementation: consult
  `/panel` on the clean approach, then surface a committed design across three
  axes: the new or defective domain terms, how the work should interact with
  existing code (including the refactors a clean design needs), and the
  domain-derived contracts the tests must keep. Run it when the work carries a
  design still unsettled — a term to work out, a contract to pin, a flow to
  shape — a judgment made fresh per piece of work. Writes no durable doc.
---

# Design

A design pass, run **after you and the operator have agreed what to build** and **before implementation**. It moves domain-design thinking ahead of implementation, so the clean approach is decided up front rather than discovered through review after the code is written. The pass consults `/panel` to sharpen the Bob across five outside lenses and runs a [prerequisite screen](prerequisite-screen.md) beside the consult, then has the Bob commit to a design along three axes and surface it to the operator. That committed design is the plan the implementation arrives with.

Whether Design runs is a judgment made fresh per piece of work, not per assignment: run the pass when the piece you are about to build carries a design still unsettled — a term to work out, a contract to pin, a flow to shape — and skip it when the approach is already settled. An assignment can hold pieces of both kinds; the judgment belongs to the piece, made at the moment you are about to build it.

**When to use:** the goal is settled (you and the operator know *what* the work is and that it serves the bigger picture) and the *how* is non-trivial. Run it in the session that will build the work: the design lives in the conversation, so the builder must be the one who holds it.

**When not to use:**

- To decide *whether* or *what* to build. That is the conversation before `/design`; this pass assumes the goal is agreed.
- Over work that carries nothing unsettled. The pass exists to close open design; run over an approach that is already decided, it can only re-derive the decision, and building the smallest thing that serves the goal cuts against that ceremony.

## The three axes

The committed design covers exactly three things, the three places where a design that was never made explicit shows up as rework in review:

1. **Domain terms.** The ubiquitous language is the domain's speech: the words a domain expert says aloud when reasoning about what the system is for. This axis asks what that speech now needs: what must the domain be able to say, after this work, that it could not say before, and which of its existing words mislead? Answer it with the Context's UL doc open in front of you, not from a memory of it. Standing comes from the speech, never from the code. A type may crystallize a sentence the domain already says ('Spawn refuses when...' becoming a `Refusal` value), but most of the records, unions, and enums a design needs are where values sit, not words anyone says: they take literate code names, stay out of the vocabulary, and leave 'Domain terms: none' a committed answer rather than a gap. The test is who would say it, not how technical it sounds: in a Context whose domain is machinery, 'origin drift' is genuine language because a spawner's expert says it aloud, while the record beside it carrying the values is honest plumbing. When the work does teach the domain a word, name it before code: a concept with no name is the most expensive thing to discover late, since two consumers each re-derive it and drift apart.
2. **Interaction with existing code.** How the work should sit in the code already there, including the refactors a clean design requires rather than bolting the new work on beside what exists. Derive from one definition; do not stand up a second consumer that re-derives what another already knows.
3. **The contracts the tests must keep.** The domain-derived promises the suite will pin, each a contract stated in domain terms (*given pieces X and Y, interaction Z produces a result with property P*), written before the modules that satisfy them.

## Procedure

### 1. Frame the design question

From the agreed goal in the conversation, state the design problem as a single question: the clean way to build this thing in this codebase. This is the question the panel will hear; conversation context stays in your head for the synthesis, not in the question.

### 2. Spawn the prerequisite screen

Spawn the screen against the framed question: one `Agent` call (subagent_type `general-purpose`, model `opus`), whose prompt is the screening prompt in [`prerequisite-screen.md`](prerequisite-screen.md) verbatim, followed by the output of `vv component-register`, followed by the design question exactly as step 1 framed it.

The screen asks the one question neither you nor the panel reliably asks, because you both reason within the task as handed: is this task hard mainly because a prerequisite is missing — often one a partner Component should own — that would collapse the task if it were built first? It runs clean-context, holding only the Component register and the question, because the agent who framed the question is the last one able to see past it. Its prompt is data in `prerequisite-screen.md`, the way the panel's gate lives in `gate.md`; tuning it is a pull request against that file.

Spawn it and move on: it runs while the panel does, and its reply — a concrete Missing / Owner / Reduces-to triple, or the single word SILENT — is not read until step 4.

### 3. Consult `/panel`

Invoke `/panel` via the Skill tool on the **design** cast, with the design question; the panel hosts more than one cast, and a programmatic caller names the one it needs rather than leaving the panel to choose. The design cast holds exactly the ground the three axes need (domain language and bounded-context boundaries, simple-design and test-first, illegal-states-unrepresentable, decomplected pieces, and the core/shell boundary), so the panel reads the design problem from the angles the axes will be answered along.

The panel is Socratic: its job is to sharpen *your* thinking, not to produce the design. You hold what the panel does not: this conversation, the actual code, and what the work is in service of.

### 4. Commit to the design

Read the panel through your own context and decide. Organize the result as the three axes above: the domain terms to add or correct, the interaction and refactors, and the contracts the tests will keep. Commit to each: a design is a position, not a survey of options. Where the panel split, say what the split turned on and which way you came down.

Collect the prerequisite screen's reply here, beside the panel. It is advisory input to this commitment, weighed with everything the screen could not see; a wrong finding costs you seconds. When a finding holds up, its triple maps onto moves you already have: file the Missing capability as its own Assignment in the Owner Component, add the Depend edge, and commit to the Reduces-to as this work's design — or, when the reduction is real but not worth the sequencing, commit to the task as posed with eyes open and say so when you surface. SILENT changes nothing.

If the pass surfaces a new or defective term, this is where the vocabulary grows or is corrected: change the Context's UL (or the framework vocabulary) as part of the design, so the name is right before the code depends on it.

### 5. Surface the committed design

Surface the committed design, tight, organized as the three axes: the residue of the pass, distilled rather than dumped. `/design` itself does not implement. The committed design lives in this conversation: implementation picks it up from here, and when a Checkpoint genuinely intervenes before the building is done, the design crosses the reseat as Carryover — it is exactly the kind of thing only the conversation built. What happens next — building now, or the operator weighing in first — is the conversation's own next move, not this skill's to fix.

## Non-goals

- **Does not write a durable design document.** The deliverable is the committed design in this conversation, not a file in the repo. A persistent design note whose purpose is to preserve a past decision is the decision-record / ADR anti-pattern the intent doctrine rules out; the *why* survives in the conversation, the PR, and the commit, not in a doc that rots as the code drifts.
- **Does not re-implement `/panel`.** It calls the shipped skill; tuning a cast is a PR against `/panel`, not a bespoke consult here.
