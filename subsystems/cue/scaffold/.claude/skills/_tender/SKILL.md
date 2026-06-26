---
name: _tender
description: >
  Machinery, not a human command: the carry-to-PR piece a procedure invokes once
  implementation has left committable changes. Run local CI, commit under the
  assignment id, push, open the pull request, and hand off to /parlay. Shared: every
  procedure that ends in a PR tenders through here rather than re-deriving it.
---

# Tender

A procedure invokes `_tender` once its implementation has left committable changes, to carry that work to a reviewed pull request. You open the PR; the merge that accepts it is the operator's, never yours. The piece is thin: plain `git` and `gh`, no project-local tooling.

## Revising a tendered PR

Once a commit is pushed, SOP is to make each later revision a new commit, never an amend or force-push over an existing one: squash-merge collapses the branch at merge, and rewriting erases the round-to-round diff. Rewrite already-pushed history only when the history contains secrets or other contamination, or when the operator asks for it.

## Procedure

### 1. Run CI locally

Run the project's CI checks. The exact commands live in `CLAUDE.md`; for Vaudeville today that is:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest
```

Fix any failures before committing.

### 2. Commit

Stage all committable changes (tracked edits and new files alike, modulo `.gitignore`) and commit with the assignment id prefixing the summary, plus a co-author trailer. `git add -u` would silently leave new files out (or commit nothing when the whole change is new files), so stage with `-A`:

```bash
git add -A
git commit -m "$(cat <<'EOF'
<ASSIGNMENT>: Summary of changes

Optional body explaining why.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3. Push

```bash
git push -u origin "$(git branch --show-current)"
```

### 4. Open the PR

If a PR already exists for the branch, skip to step 5. Otherwise:

```bash
gh pr create --title "<ASSIGNMENT>: Summary of changes" --body "$(cat <<'EOF'
## Summary

- One bullet per change

Assignment: <ASSIGNMENT>

## Test plan

- [x] CI green locally
EOF
)"
```

### 5. Verify CI

Wait for the CI run **for the commit you just pushed** before handing off, not the branch's most-recent run. Keying the poll on `--branch ... --limit 1` races: right after a push, `gh run list` can return a prior commit's already-green run before GitHub has enqueued the workflow for the new commit, and the gate would read that stale success as this commit's verdict. Step 3 pushed HEAD and step 4 added no commit, so HEAD is the pushed commit; key the poll on its SHA. (`gh pr checks` is the obvious command but fails under the current token scope; the workflow-runs endpoint is readable.)

```bash
pushed_sha=$(git rev-parse HEAD)
gh run list --workflow=ci.yml --commit "$pushed_sha" --limit 1 \
  --json databaseId,status,conclusion,url
```

Interpret the result:

- **Empty `[]`** → GitHub has not enqueued the workflow for this commit yet. Wait a few seconds and re-poll. Empty is not green.
- **`status` anything other than `completed`** (e.g. `queued`, `in_progress`, `requested`, `waiting`, `pending`) → the run is still going; keep polling until it completes. `conclusion` is `null` until then, so do not read it yet.
- **`status: completed`, `conclusion: success`** → proceed to step 6.
- **`status: completed`, any other `conclusion`** → fetch logs with `gh run view <databaseId> --log-failed`, diagnose, fix locally, and re-run from step 1. If the fix is substantial enough to change the design picture, the calling procedure's closing Doctrine Bracket read applies again before you continue.

### 6. Hand off to `/parlay`

CI is green for the pushed commit. Invoke `/parlay` via the Skill tool with no arguments (the last thing you do here). It checkpoints again and runs the convergence loop in a fresh context; you do not run the loop yourself.

`/parlay`'s Report is the single end-of-lifecycle report to the operator. Do not emit a separate "PR opened at X" message before handing off. The assignment is not done until the operator reviews and merges the PR.

## On failure

If any step fails and you cannot resolve it, stop and return to the operator with which step failed, the error output, and what you tried. Do not retry indefinitely: a stuck tender is usually a sign the work was not as settled as the procedure assumed.
