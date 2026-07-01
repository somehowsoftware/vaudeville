---
name: incident-report
description: >
  The operator flagged an incident and told you to file a report on it. Fill the
  `vv incident-report` form with what you OBSERVED — not the cause, not a fix — and
  run it. You do not diagnose and you do not investigate.
model: opus
effort: low
---

# Incident report

Write down what you *observed* and hand it off — you do not work out the cause and you do not fix the thing. A later, clear-headed reader diagnoses it from your session transcript; your report is only the index that leads there. The pull is to explain the cause that looks obvious from inside the failure, or to just fix it and move on. Both are the confident-wrong move this exists to keep out.

## Fill the form

`vv incident-report` files the report from two fields, and nothing else:

- **`--problem`** — what happened, as observed: the instruction you read, the action you took, the signal that came back. Facts, then stop. No cause, no "what I'd look at," no fix.
- **`--summary`** — the incident as a flat event (*checkpoint failed twice in one session*), not a lesson or a cause.

Add **`--assignment <ID>`** and **`--session <ID>`** when you have them: the reader finds your transcript through them, and teardown may move the worktree the command captures. Build both fields through single-quoted heredocs so the backticks and other metacharacters in your observed text stay literal:

```bash
summary=$(cat <<'INCIDENT_SUMMARY'
<the incident, named flatly as an event>
INCIDENT_SUMMARY
)
problem=$(cat <<'INCIDENT_PROBLEM'
<what went wrong, as observed: no cause, no fix>
INCIDENT_PROBLEM
)
vv incident-report --summary "$summary" --problem "$problem" [--assignment <ID>] [--session <ID>]
```

It prints the new id and files under the cwd Component unless you pass `--project <PREFIX>`. Then stop: report the id, and do not investigate, fix, or spawn.
