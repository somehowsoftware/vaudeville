---
name: command
description: >
  File a Command (a directive the operator has settled and wants carried out)
  into the tracker, in this thread. Compose the ordered steps and authorization
  gates with the operator, ask about anything unclear, and invent nothing.
  Operator-invoked.
model: opus
effort: medium
---

# Command

A **Command** is the Assignment whose *ends* and *means* are both settled: a directive the operator has decided on and is handing off to be carried out. The authority is the operator's: a Command always comes from them, and an agent never makes one up on its own. You file one the operator dictates to you, or one that `/premise`'s gate sent here because the agent was holding the operator's settled directive rather than a claim of its own. Your job is to write down what they have settled, accurately enough that the agent who runs it later does the right thing.

A Command is the steps the operator wants taken and the authorization gates they want held: points where the agent running it must stop for a go-ahead before doing something irreversible. That agent brings its own judgment to the *how*; the Command gives it the goal and the boundaries, not a script that does its thinking for it. "Make this config change" or "run this spike and report back" is a Command: a directive settled enough to execute. If the operator means to stay on the wheel and steer as the work unfolds, that is a `/manual`, not a Command.

## Record what was settled; invent nothing

You are capturing the operator's settled intent, not writing a proposal of your own. A Command is supposed to read like orders (that is what it is) so the steps themselves are never the danger. The danger is a step the operator never gave you: it carries their authority without their intent, and the agent who runs the Command later, with context you do not have, has no way to tell it from the rest. Write down what they settled, and nothing more. You are a courier here, not an author.

- Where the directive is unclear or underspecified, **ask the operator**, even if it feels like nagging.
- The operator may answer "decide that when you implement it." That is a real answer: write the Command so it says the detail will be chosen during implementation.
- Every detail you are about to write, check against what the operator actually asked for. A detail they never asked for (added because it seems helpful, or to round out the steps) is the worst thing you can put in a Command: it carries the operator's authority without their intent and sends the implementer somewhere they were never sent. Cut it.

A Command is a one-time-use skill. Constrain it too tightly and you waste the intelligence of the agent running it; leave the right room and it does the job well.

## Procedure

### 1. Compose the title

One line naming the directive: what the operator wants done.

### 2. Compose the body with the operator

Write the ordered steps the operator settled and the authorization gates they want. Where they deferred a detail to implementation time, say so in place rather than filling it in.

### 3. Choose the Route

`check-in` by default: the agent running it surfaces a check-in before the work merges. Choose `direct` only if the operator explicitly says the Command should run to completion without one.

### 4. File it

Carry the title and body through single-quoted heredocs so backticks and other shell metacharacters do not interpolate:

```bash
summary=$(cat <<'COMMAND_SUMMARY'
<the title from step 1>
COMMAND_SUMMARY
)
description=$(cat <<'COMMAND_BODY'
<the steps and gates from step 2>
COMMAND_BODY
)
new_id=$(vv command --project <PREFIX> --summary "$summary" --description "$description" [--route direct] [--dep <PEER>...])
```

Each closing delimiter sits at column 1 with no leading whitespace. `--project` is the Component the directive's work belongs in. `--route` defaults to `check-in`. `--dep` wires a prerequisite the Command waits on; use it when the operator wants the Command to run only once some other work has merged. `vv command` prints the new Command's idReadable.

### 5. Report

One line: the new Command's id and its Route. The Command waits in the tracker until the operator signs it off.

## Non-goals

- **Does not spawn or run.** `vv command` has no `--spawn`; filing a Command never starts it. A Command carries the operator's authority, so it waits outside the pool until the operator signs off (`/sign-off`): the release that admits it for spawn.
