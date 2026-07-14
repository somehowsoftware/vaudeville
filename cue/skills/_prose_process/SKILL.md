---
name: _prose_process
model: opus
description: >
  Machinery, not a human command: the prose specialization of the
  design-bracketed path the /realize router dispatches to. It partitions an
  assignment's prose into reader-situations, composes each through `/prose`, then
  delivers once. It holds no prose craft of its own; the composing lives in
  `/prose` and its bookends. Reached only after /realize has judged the task.
---

# Prose process

The prose specialization of the design-bracketed path. [`/realize`](../realize/SKILL.md) dispatches here for any agent-facing prose composition. This procedure owns three things and no more: cutting the assignment into pieces, composing each, and delivering the result once. The composing itself is not here; it is in [`/prose`](../prose/SKILL.md) and the bookends `/prose` calls. Everything that was once craft has left this procedure, which is why it earns its underscore: what remains is sequencing.

## 1. Ground in the assignment

Read the assignment whole and the prose it touches, enough to see the work's shape and where its pieces fall. The per-piece grounding (the doctrine, the interaction space of each piece) belongs to `/prose`; here you need only enough of the whole to partition it well.

## 2. Partition into reader-situations

Cut the assignment's prose into groups, one per [reader-situation](../../docs/vocabulary.md): prose that shares a reader, a purpose, and a frame, such that a single framing and a single assay serve it. The cut is by reader, not by file. Two files that are one argument to one reader are one group; one file addressing two genuinely different readers can be two. Often the answer is one group, and that is fine; let the count follow the work, never a shape imposed on it. This partition is the only judgment this procedure carries; everything after it is a loop and a delivery.

## 3. Compose each group

For each group, invoke `/prose` via the Skill tool: it composes that one coherent piece for that one reader-situation and stops at a finished piece, without delivering. Compose the groups in whatever order their dependencies require.

A long run over several groups can fill the context the way any long session does. If it tightens, take a bare `/checkpoint` between groups to carry the finished pieces and the remaining partition into a fresh context, then continue. This is judgment, not a step: one or two groups need none.

## 4. Deliver once

When every group is composed, invoke `_tender` via the Skill tool with no arguments: local CI, commit under the assignment id, push, the single pull request over all the pieces, and the hand-off to [`/parlay`](../parlay/SKILL.md). One assignment, one delivery, however many pieces it took to compose. Invoking it is the last thing you do here.
