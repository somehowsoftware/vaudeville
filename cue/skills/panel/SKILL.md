---
name: panel
model: opus
description: >
  Put a question to a named cast of opinionated lenses in parallel, then think
  through their responses yourself and surface to the operator a distilled
  synthesis plus your own take. The cast (a roster of lenses chosen for a kind
  of question) is data under `casts/`; the panel is the mechanism that runs
  whichever cast fits. The panel is input for *your* thinking; the operator's
  attention is scarce and gets the residue, not the raw responses. Often
  Socratic: the panel exists to sharpen the invoking agent's thinking, not to
  produce a report.
---

# Panel

Put a question to a **cast** of strong-lens panelists in parallel. Read their responses. Think them through against everything you know about the situation that the panel doesn't. Write the operator a tight synthesis with your own committed take, and write the raw responses to a transcript file in case anyone wants to dig.

A cast is a named roster of lenses, each a paragraph of what one thinker sees and looks for, written so the panelist inhabits the frame. Casts are data (one file apiece under `casts/`) and the panel is the mechanism that runs whichever cast fits the question. This skill names no lens and counts none of them; the lenses and their number live in the cast.

The point is often **Socratic**: the panel exists to make *you* think through the problem from several outside angles, not to deliver a multi-act reading to the operator. The report to the operator is the residue of that thinking, not a transcript of it. Treat the operator's attention as the scarcest resource in the room.

**When to use:** you're chewing on something (a design question, a rule under examination, a code review, a debugging dead end) where one voice deep isn't enough and a few outside reads through strong lenses would sharpen your thinking.

## How this skill works

One parallel `Agent` call per lens in the chosen cast (subagent_type `general-purpose`), each carrying that lens's prompt. Each panelist runs clean-context; they see only their lens + the question, never this conversation. The clean context is the point: if the panelists carried the conversation's framing into their turn, the panel collapses into echo.

After they return, *you* synthesize. You hold what the panel doesn't: this conversation, the code under discussion, what the work is in service of. There is no separate synthesizer Agent; that role would have a context blinder you don't. You read the panel, integrate it with what you already know, form a take, and tell the operator tightly.

Before any of that, the question is screened. Clean context stops the panel inheriting your framing through the conversation, but it cannot stop a question that carries the framing in its own words (a contested claim stated as a given, one option pre-discredited, the wanted answer priced) because to a clean reader a planted premise is just a premise to reason within. The agent that wrote the question cannot catch this either; the party holding a prior is the last to see it in its own words. So a separate clean-context gate screens the question first, and only a clean verdict spawns the panel. The gate's prompt is data, in [`gate.md`](gate.md), the way the casts are.

## Procedure

### 1. Resolve the cast and the question

The **question** is either `$ARGUMENTS` (when invoked as `/panel <question>`) or the question being chewed on in this conversation. If ambiguous, ask one short sentence to pin it down; do not guess. The question goes to the panel verbatim. Strip framing, caveats, "for context." Conversation context lives in your head and informs *your* synthesis, not the panelists'.

The **cast** is resolved one of two ways:

- **A programmatic caller names it.** A skill that invokes the panel knows which cast it needs and says so. Design, for one, always runs the `design` cast. When the invocation names a cast, run that cast; do not second-guess a caller that named one.
- **A bare interactive invocation names none.** Then *you* choose: read the `**Purpose:**` line near the top of each `casts/*.md`, and pick the cast whose purpose fits the question. Choosing is a semantic classification (which kind of question is this) so **name your pick** in the conversation before you spawn, where the operator can see it and correct it. If no cast's purpose fits the question, say so and **halt**: there is no default cast, and running the nearest-fit one wastes tokens and skews your synthesis.

### 2. Screen the question for a loaded frame

Before spawning anyone, hand the question to the gate. In one `Agent` call (subagent_type `general-purpose`, model `opus`, since the screen turns on subtle judgement and runs on the strong model), pass the contents of [`gate.md`](gate.md) verbatim, then the question exactly as it would reach the panel, context block included. The gate returns a verdict.

- **CLEAN**: proceed to the panel.
- **RIGGED**: do not spawn. The gate returns the tells and a neutral rewrite; take the rewrite (sharpen it if you must, but do not reintroduce what it stripped) and screen the result again. Only a CLEAN verdict authorises the panel.

The gate runs clean-context for the reason the panel does, turned on you: you wrote the question, so you are the last one able to see the prior you built into it. The clean verdict is the gate's to give, not yours. You may not wave your own question through. This binds every invocation, a programmatic caller's cast question as much as an interactive one.

### 3. Spawn the panelists in parallel

In a **single message**, make one `Agent` tool call per lens in the cast.

Each Agent call uses:
- `subagent_type`: `general-purpose`
- `model`: `opus`, since each voice runs the same tier as the synthesis turn, the skill's frontmatter model.
- `description`: `Panel: <lens name>`
- `prompt`: the lens's prompt from the cast file verbatim, followed by `## The question` and the question verbatim, followed by the response-format suffix below.

The cast's lens prompts are doctrine. Use them verbatim. Tuning belongs in PRs against the cast file, not at invocation time.

#### Response-format suffix (append to every lens prompt)

```
## Response format

Two short paragraphs maximum. Take a position; don't survey options.
Don't hedge. The agent reading the panel will note where you disagree
with the others. Your job is to say what your lens sees, not to
anticipate the others.
```

### 4. Write the transcript

Once all panelists return, write the raw transcript to `/tmp/panel-<YYYYMMDD-HHMMSS>.md`: a `# Panel: <question>` title, then one `## <lens name>` section per lens carrying that panelist's response, in the cast's order.

The transcript is the receipt. The operator may never open it; that's fine. It exists so that "if I want more detail about what a panelist said, I'll ask or just look" is a real option.

### 5. Synthesize and form a take

Read the panel through your own context. You hold what the panel doesn't: the conversation that prompted the question, the code under discussion, the work this is in service of. The synthesis is yours, not one more lens.

You owe the operator two things:

1. **The synthesis.** Where the panel converged, where they split, what each split actually turns on (a value judgment? an empirical question? a difference in scope?). Name panelists when their claim is decisive; skip naming them when it isn't. Don't quote them at length. Paraphrase tight.
2. **Your take.** Having read the panel through your context, what do you now think? Commit. Don't hedge into surveyor-mode. The operator asked for a take, not a survey of options.

### 6. Report

Print to the conversation, in this shape:

```
**/panel (<cast>): <question>**

<synthesis, ~150-200 words, with panelist attributions only where decisive>

**My take:** <your view, ~50-100 words, committed>

*Transcript: /tmp/panel-<timestamp>.md*
```

That's the whole output. Don't paste any panelist's response into the report. The transcript holds those. If the operator wants depth, they'll open the file or ask.

## Casts

The casts live under `casts/`, one file each: a `**Purpose:**` line the [selection step](#1-resolve-the-cast-and-the-question) reads to judge fit, then the cast's ordered roster of lens prompts. A new cast is that one file; this mechanism does not change to accommodate it.
