---
name: _continue_materialize
description: >
  Machinery, not a human command — the continuation `/materialize` checkpoints into.
  Make a planned Premise real: implement, then land it, in the fresh context the
  checkpoint resumed you into. Two shapes — CI-gated Premises run local CI, commit,
  push, open a PR, and hand off to /parlay; off-tree Premises (clean working tree)
  report and stop.
---

# Continue materialize

The leading underscore marks machinery: this skill is sent by the checkpoint driver into the freshly cleared session, immediately after the `/clear`. A human reaching for materialization wants `/materialize`, the thin entry; nobody types this by hand.

## You arrive grounded

This skill is invoked by the Resume Brief — the first turn of this cleared session, already in the conversation above. It carries the operator's verbatim turns (the Digest) and your own Carryover, which holds the committed implementation plan; you read both on the way here, and there is nothing to fetch. Honor the Brief's discipline throughout the procedure: the latest operator turn is the live one, the Carryover's pointers are load-bearing, and any doctrine or domain term you lean on gets re-read from its source — a cleared context presents as fluency, not as ignorance. If no Resume Brief sits above you, something invoked this skill out of band; stop and say so rather than improvise grounding.

## Implement, then land it

`/_continue_materialize` *is* the implementation — you arrive with the plan in the Carryover and this skill turns it into reality, then lands it. It is not a packaging step you reach for after writing code ad hoc: implementation is its first move, not a precondition. Two shapes follow from what the work produces: a CI-gated branch for Premises that leave committable changes in the working tree, an off-tree branch for Premises whose deliverable lives outside git.

**When to use:** mechanical Premises where the full author / review / ghostwrite pipeline adds overhead without proportional value. `/materialize` handles both of the following shapes:

- **CI-gated Premises** with code worth versioning — dependency updates, formatting fixes, typo corrections, configuration changes, doc edits.
- **Off-tree Premises** whose deliverable lives outside the git tree — tracker-only cleanups, infra configuration, third-party state changes.

Step 2's working-tree check picks the branch from the implementation's actual product. The author of the Premise does not declare the shape in advance.

This skill is intentionally thin: it uses plain `git` and `gh`, no project-local tooling. As the lifecycle tooling matures, individual steps here will be replaced by skill-specific tooling.

## Procedure

### 1. Re-read the doctrine

Before you write, **re-read the design Doctrine** (currently `~/.vaudeville/doctrine/code/design.md`). Actually re-read it. Open the file and input its content as tokens, directly from the file, now. You have already read it during priming, but as only one of several documents. Since then, you have had at least one turn, and likely you have had more than one. You will **re-read** it now. You will not refuse because you have "already read it." If you do not re-read it, you have already failed at the execution of the skill.

### 2. Implement

The committed approach is in the Carryover, in the Resume Brief above — the design `/design` produced, or what you and the operator agreed before the checkpoint cleared that conversation. Implement that, rather than re-deriving the articulation below. (The Doctrine Bracket's re-reads, Step 1 and Step 4, still apply.)

Having **re-read** the doctrine, you must articulate to yourself, in chat:

- How the Premise's intended domain logic maps onto the existing ubiquitous language — the framework UL at `~/.vaudeville/doctrine/vocabulary.md`, and the bounded context's local UL if it has one (typically `docs/vocabulary.md`).
- What new UL terms, if any, the work needs. Grow the vocabulary first if so. 
- What structure will leave the codebase easier to work in next week than this week — pieces named in domain terms, modules each owning exactly one piece, contracts written as tests before the modules that satisfy them, names that hit the reader over the head.

If the strategy is unclear, spiking is acceptable — but the spike must then be **replaced** (not patched) with domain-oriented code driven by behavioural tests written first.

**As a reminder: implementation details are not domain concepts. Domain concepts are domain concepts. Adding implementation details to the UL is contamination. Do not do this.**

Implement the changes from the context brief.

This is the opening half of the **Doctrine Bracket** — the design-Doctrine read that frames the work before you write; Step 4 is the closing half.

### 3. Branch on working-tree state

After implementation, check whether the working tree has any committable changes — tracked modifications, staged changes, or new untracked files (modulo `.gitignore`). The standard idiom is `git status --porcelain`, whose stdout is empty exactly when the tree is clean:

```bash
test -z "$(git status --porcelain)"
```

- **Non-zero exit (working tree has changes)** → continue with Step 3, the CI-gated branch.
- **Zero exit (working tree clean)** → skip to Step 10, the off-tree branch.

`git diff --quiet HEAD` is the obvious shorter form but it ignores untracked files; a Premise that creates new files (and modifies none) would be misclassified as off-tree and lose its deliverable. `git status --porcelain` covers tracked, staged, and untracked alike, which is what the predicate actually wants.

The working-tree state is the source of truth for which shape the Premise takes; do not declare the shape in advance and do not override the branch decision here. If the implementation should have produced changes but did not (forgotten save, refactor that turned out to be a no-op), `/closeout delivered`'s synopsis step refuses a vacuous closeout when the agent has captured no evidence — that is the layered guard, one observation point downstream.

### 4. Re-read the design Doctrine _again_

Re-read the design Doctrine (currently `~/.vaudeville/doctrine/code/design.md`) with the diff in hand. Again, you must actually open the file and read it. It is irrelevant that you have "already read it" in the past. Good! Read it again, now.

Ask whether the PR you are about to open is in service of the design discipline's stated goals:

- Pieces named in domain terms, not in implementation verbs.
- Each module owning exactly one piece — no orchestrator-shaped vacancies threading state across phases.
- Contracts written as tests before the modules that satisfy them.
- Names that hit the reader over the head, drawn from the ubiquitous language.
- Technical surplus on net — easier to work in next week than what was there before.

If any answer is no, **revise before continuing**. The cost of revising now is a re-run of local CI; the cost of revising after `/parlay` is a Codex round-trip, an angry operator, and/or an avoidable follow-up Premise. CI green is not a surplus deposit, and the diff is what the operator will read.

This is the closing half of the **Doctrine Bracket**; Step 1 opened it.

### 5. Run CI locally

Run the project's CI checks. The exact commands live in `CLAUDE.md`; for Vaudeville today that is:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest
```

Fix any failures before committing.

### 6. Commit

Stage all committable changes — tracked edits and new files alike, modulo `.gitignore` — and commit with the Premise ID prefixing the summary, plus a co-author trailer. Step 3 routes new untracked files into this branch, so the stage must include them; `git add -u` would silently leave them out (or commit nothing when the whole change is new files):

```bash
git add -A
git commit -m "$(cat <<'EOF'
<PREMISE>: Summary of changes

Optional body explaining why.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

### 7. Push

```bash
git push -u origin "$(git branch --show-current)"
```

### 8. Open PR

If a PR already exists for the branch, skip to Step 8. Otherwise:

```bash
gh pr create --title "<PREMISE>: Summary of changes" --body "$(cat <<'EOF'
## Summary

- One bullet per change

Premise: <PREMISE>

## Test plan

- [x] CI green locally
EOF
)"
```

### 9. Verify CI

```bash
gh run list --workflow=ci.yml --branch "$(git branch --show-current)" --limit 1 \
  --json databaseId,status,conclusion,url
```

Poll until `status` is `completed`. PROCEED on `conclusion: success`; on any other conclusion, fetch logs with `gh run view <databaseId> --log-failed` and fix. (`gh pr checks` is the obvious command but fails under the current token scope; the workflow-runs endpoint is readable.)

**On CI failure:** diagnose and fix locally, then re-run CI from Step 4. If the fix is substantial enough to change the design picture, re-do Step 3 first.

### 10. Hand off to `/parlay`

CI is green for the pushed commit. Invoke `/parlay` via the Skill tool with no arguments — that is the last thing you do here. `/parlay` is the thin entry: it checkpoints again, and from its `vv checkpoint` call an external process drives a second clear and activates `/_continue_parlay`, which runs the convergence loop. That second clear is the control handoff to parlay doing its job, not an extra step; you do not run the loop yourself.

`/parlay`'s Report is the single end-of-lifecycle report to the operator — do not emit a separate "PR opened at X" message before handing off. The Premise is not done until the operator reviews and merges the PR.

### 11. Off-tree terminus — report and stop

The implementation produced no commit-worthy artifact: nothing to push, no PR to open, no CI run to track. The Premise's deliverable lives outside the git tree. Summarise the captured evidence from the conversation — which API calls ran, what changed in the target system, what deviated from the Premise as written — and report that the Premise landed off-tree.

## On failure

If any step fails and you cannot resolve it, stop and return to the operator with which step failed, the error output, and what you tried. Do not retry indefinitely — shippable work should be straightforward, and a stuck shipper is usually a sign the gate assignment was wrong.
