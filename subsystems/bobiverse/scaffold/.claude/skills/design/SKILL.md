---
name: design
model: opus
description: >
  Run a design pass after the goal is agreed and before `/materialize`:
  consult `/panel` on the clean approach, then surface a committed design
  across three axes — the new or defective domain terms, how the work should
  interact with existing code (including the refactors a clean design needs),
  and the domain-derived contracts the tests must keep. The design lives in
  the conversation `/materialize` implements; it writes no durable doc.
---

# Design

A design pass for the Bob lifecycle, run **after you and the operator have agreed what to build** and **before `/materialize`**. It moves domain-design thinking ahead of implementation, so the clean approach is decided up front rather than discovered through review after the code is written. The pass consults `/panel` to sharpen the Bob across five outside lenses, then has the Bob commit to a design along three axes and surface it to the operator. That committed design is what `/materialize` then implements.

`/design` is optional. Reach for it when the work is substantial enough that the clean approach is worth getting right before code — a new concept, a refactor, a change with more than one defensible shape. Mechanical Premises that go straight to `/materialize` do not need it.

**When to use:** the goal is settled — you and the operator know *what* the work is and that it serves the bigger picture — and the *how* is non-trivial. Run it in the same Bob that will run `/materialize`; the design it produces is the plan `/materialize` arrives with.

**When not to use:**

- To decide *whether* or *what* to build. That is the conversation before `/design`; this pass assumes the goal is agreed.
- For mechanical work whose shape is obvious. The design pass must not become its own source of after-the-fact revision — building the smallest thing that serves the goal cuts against a heavyweight pass.

## The three axes

The committed design covers exactly three things — the three places where a design that was never made explicit shows up as rework in review:

1. **Domain terms.** What new ubiquitous-language terms the work introduces, and which existing terms it shows to be defective or mis-scoped. A concept with no name is the most expensive thing to discover late: when a piece is never named, two consumers each re-derive it and drift apart. Name the missing piece — or correct the defective term — before code, and grow the vocabulary first.
2. **Interaction with existing code.** How the work should sit in the code already there, including the refactors a clean design requires rather than bolting the new work on beside what exists. Derive from one definition; do not stand up a second consumer that re-derives what another already knows.
3. **The contracts the tests must keep.** The domain-derived promises the suite will pin — each a contract stated in domain terms, *given pieces X and Y, interaction Z produces a result with property P* — written before the modules that satisfy them.

## Procedure

### 1. Frame the design question

From the agreed goal in the conversation, state the design problem as a single question — the clean way to build this thing in this codebase. This is the question the panel will hear; conversation context stays in your head for the synthesis, not in the question.

### 2. Consult `/panel`

Invoke `/panel` via the Skill tool with the design question. The five-lens cast holds exactly the ground the three axes need — domain language and bounded-context boundaries, simple-design and test-first, illegal-states-unrepresentable, decomplected pieces, and the core/shell boundary — so the panel reads the design problem from the angles the axes will be answered along.

The panel is Socratic — its job is to sharpen *your* thinking, not to produce the design. You hold what the panel does not: this conversation, the actual code, and what the work is in service of.

### 3. Commit to the design

Read the panel through your own context and decide. Organize the result as the three axes above: the domain terms to add or correct, the interaction and refactors, and the contracts the tests will keep. Commit to each — a design is a position, not a survey of options. Where the panel split, say what the split turned on and which way you came down.

If the pass surfaces a new or defective term, this is where the vocabulary grows or is corrected: change the bounded context's UL (or the framework vocabulary) as part of the design, so the name is right before the code depends on it.

### 4. Surface and stop

Surface the committed design to the operator, tight, organized as the three axes — this is the residue of the pass, the way a check-in is the residue of its discussion. Then stop. The design lives in this conversation; `/materialize` reads it from here when the operator runs it. `/design` does not implement and does not invoke `/materialize` — the operator pulls that trigger when the approach is baked.

## Non-goals

- **Does not implement.** `/materialize` does. `/design` produces the approach `/materialize` arrives with.
- **Does not write a durable design document.** The deliverable is the committed design in this conversation, which `/materialize` inherits — not a file in the repo. A persistent design note whose purpose is to preserve a past decision is the decision-record / ADR anti-pattern the intent doctrine rules out; the *why* survives in the conversation, the PR, and the commit, not in a doc that rots as the code drifts.
- **Does not re-implement `/panel`.** It calls the shipped skill; tuning the panel cast is a PR against `/panel`, not a bespoke consult here.
- **Does not settle the goal.** The goal is agreed before `/design` runs.
