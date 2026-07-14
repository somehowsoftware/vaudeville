---
name: _off_tree_process
description: >
  Machinery, not a human command: the off-tree realization procedure the
  /realize router dispatches to. For work whose deliverable never touches the
  git tree: tracker mutations, infrastructure or third-party state changes,
  process actions. It produces no pull request; it executes the action and hands
  to closeout's no-PR delivered path. The thinnest of the procedures.
---

# Off-tree process

[`/realize`](../realize/SKILL.md) dispatches here when the change you have worked out is real but produces nothing in the git tree: a tracker field mutation, an infrastructure or third-party state change, a process action whose result lives in another system's state rather than in a diff. There is nothing to commit, so there is no pull request and no [Tender](../_tender/SKILL.md). If the work turns out to produce a git artifact after all, the router sent you here in error: that work tenders; go back to [`/realize`](../realize/SKILL.md).

## Stay grounded

There is no reviewer downstream and no merge gate to catch a misstep, so the Doctrine binding you is the whole of the discipline on this action. You are the last line. The bearing (`~/.vaudeville/doctrine/bearing/`) binds every move, and the one that bites hardest here is that you build the smallest thing that serves the goal: the smallest set of state changes that delivers the assignment, nothing speculative. An off-tree action leaves no diff for anyone to read after the fact, so the care you put into surfacing it carries the weight a PR description would carry on the tree.

## Execute

Take the action, capturing what happened as you go: the commands run, the responses returned, the state observed before and after. That capture is the only record of an off-tree action, and what closeout reads in place of a diff.

If execution fails partway, stop and surface the partial state plainly. An off-tree action has no atomic commit and no rollback, so a half-applied change is real state the operator needs to see exactly: how far it got, and what is now inconsistent.

A divergence is subtler than a failure: the action can still go through, but a discovery mid-execution makes you want to deviate from what you were dispatched to do. Dispose of it before you act, not by carrying it forward — there is no pull request here and no review downstream, and the act itself is the irreversible, external change, so nothing catches a wrong turn after the fact. Return to the operator a discovery that would have you commit state the operator-aligned plan did not sanction, or that overturns the goal you were sent to realize; a judgement call that stays within that plan you make yourself, building the smallest thing that serves the goal.

## Close

There is no PR to merge, and nothing downstream will record this assignment delivered, so recording it is yours. Invoke `/closeout delivered`, putting the capture from Execute into its synopsis as the durable account of what changed.
