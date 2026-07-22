---
name: tender
description: >
  Carry finished work to a pull request and present it for acceptance: run local
  CI, commit under the assignment id, push, open the PR, and watch its CI for the
  pushed head — or report honestly when the repository runs none. The merge that
  accepts a tender is never your own act; presenting is not completing, and
  whether the merged PR is the goal or a station on the way is the goal's own
  question.
---

# Tender

Invoke `tender` once implementation has left committable changes, to carry that work to a reviewed pull request. Carry it the whole way: a tender ends with the PR open and reported, never with a request for permission to open one. You open the PR; the merge that accepts it is the operator's, never yours.

The steps are ones you already know how to do in any repository: the project's own checks run locally and pass before anything is committed; the assignment id prefixes the commit summary and the PR title (`<ASSIGNMENT>: summary`), and the commit carries a co-author trailer; the branch pushes; the PR opens, or the branch's existing PR updates. What this skill holds is the judgment around those steps:

- **The verdict you report is the pushed head's, not the branch's.** A branch-keyed look at CI can hand you a prior commit's green while the new head's run is still enqueuing; key what you watch to the commit you pushed. And report what actually happened for that head: a repository that defines no CI, or whose workflows do not fire for this push, gets that said plainly in the report — bounded patience, never an open-ended wait on a signal that may not come.
- **A red run is a symptom before it is an edit.** Digest the failing log in a context you discard, then ask what about the change lets the failure exist, not just what silences the check. By around the third forced diagnose-and-fix round on one tender, the defect is usually no longer what limits the work — the framing is; stop and bring the operator what the rounds showed.
- **Revisions are new commits, never a rewrite.** Squash-merge collapses the branch at merge anyway, and a force-push erases the round-to-round diff a reviewer reads. Rewrite pushed history only for contamination such as a leaked secret, or when the operator asks.
- **Report once, in one message:** the PR, the pushed head's CI verdict, and anything the rounds surfaced. The merge is acceptance of the work, not necessarily the end of it: whether the goal is satisfied at the merge or runs past it is the goal's question, already yours from the first turn.

If a step fails and you cannot resolve it, stop and return to the operator with what failed and what you tried; a stuck tender usually means the work was less settled than it looked.
