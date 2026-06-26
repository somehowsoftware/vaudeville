---
name: tmp
description: >
  Read the `tmp` file where the operator responds to numbered paragraphs from
  long chat turns. Parses numbered responses and freeform commentary.
---

# Tmp

Read the file `tmp` at the worktree root. The operator uses this file to respond to long chat turns that use hierarchical paragraph numbering (e.g., **1.1**, **3.2**); check-in route outputs are the most common, but the same pattern fits any multi-paragraph turn.

## Step 1: Read

Use the Read tool (not cat) to read `./tmp`.

## Step 2: Parse

The file contains two kinds of content:

**Numbered responses**: lines that start with a paragraph number matching your previous output's numbering (e.g., `1.2`, `3.1`, `5.2`). Examples:

```
1.2: we settled on Predicate, not Filter
3.1 yes
5.2: defer this, it's speculative
```

The number maps back to a paragraph you wrote. A colon or space after the number separates it from the response. Match each number to the corresponding paragraph in your previous output; you already have that output in context, so no file lookup is needed.

**Freeform commentary**: lines that do not start with a paragraph number. These are general thoughts, new topics, or observations not tied to a specific paragraph:

```
also I noticed the spec still says Swift in section 12
```

If your previous output did not use numbered paragraphs, treat the entire file as freeform commentary.

## Step 3: Respond

Respond to each item substantively:

- For numbered responses, address the specific paragraph the operator is commenting on. Reference the original content so the response is grounded.
- For freeform commentary, treat it as a new topic the operator is raising.
- Do NOT just echo the contents back. Engage with the substance: answer questions, adjust your approach, flag disagreements.
- Put a blank line between every pair of paragraphs in your response. The operator reads chat in a TUI that renders adjacent paragraphs as a single undifferentiated block when the blank line is missing; the numbered turns produced by this skill are exactly the long turns that suffer most. Treat this as a discipline on par with Markdown spec compliance, not a stylistic preference.

## Numbering Convention: Restart at 1, Use Bold-Dot, Reference in Prose

Each agent turn restarts paragraph numbering at **1**, and the marker is written in bold-dot form (`**1.**`, `**2.**`, `**3.**`, or hierarchical `**1.1**`, `**2.3**`) at the start of each paragraph. There is no cross-turn letter prefix. When you need to refer back to something (the operator's earlier paragraphs, your own earlier paragraphs, anything from upthread), write the reference in **explicit prose** somewhere inside the paragraph that needs it (a single-sentence snippet shown here, not a full paragraph):

- "[...] My earlier claim that the walker has to traverse imports no longer holds; the AST library exposes them directly. [...]"
- "[...] Returning to your point about cross-tenant isolation, the consequence is that the worktree path can't be derived from the Assignment id alone. [...]"
- "[...] I still disagree about merging the two Routes, for the constraint you raised at the top of this thread: a `plan` Assignment's deliverable is in the tracker, not in a PR. [...]"

Two reasons for the bold-dot form, both essential:

- **It dodges the TUI's list-marker classifier.** Bare `1.` `2.` `3.` at line start is parsed as a CommonMark ordered list; the Claude Code renderer then applies compact item spacing and collapses the blank lines between paragraphs no matter what the source contains. The wall the operator sees is the renderer doing this, not the agent skipping blank lines. The leading `**` breaks the list-pattern match, so bold-dot paragraphs render with paragraph spacing. `(1)` and `¶1.` also dodge the classifier; bold-dot was picked because it reads as a numbered paragraph at a glance.
- **The trade-off in numbering style is deliberate.** Letter prefixes were compact but forced the reader to reconstruct context from a position index. Prose references are slightly longer but each turn is self-contained; the operator can read any turn in isolation and know what it refers to without paging back.

The operator's own `/tmp` replies continue to use bare numbers (`3: yes`, `5.2: defer this`). Their responses are not multi-paragraph chat turns, so the rendering bug doesn't apply, and the bare-number form is what the parser in Step 2 of this skill expects. Their turn always refers to your most-recent output, so no prefix is needed.

## Trailing Skill Invocation

If the `/tmp` file ends with a skill invocation (e.g., `/blueprint`, `/review`), treat it as the operator intending to trigger that skill after you have addressed the numbered and freeform content above it. Process all responses first, then invoke the trailing skill.
