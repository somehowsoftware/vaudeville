# Driving other Bobs through workmux

Sometimes an agent (a human operator, or a Bob acting as one) needs to launch a
second Bob and then puppeteer it: send it instructions, watch what it does, wait
for it to reach a state. The whole mechanism runs through **workmux** (the
worktree + tmux orchestrator) plus a few facts about how Claude Code stores and
resumes sessions. This page is the standing recipe for both halves: getting a
Bob running in a workmux window, and driving one that is already running.

The happy path for *spawning a Bob on an Assignment* is `vv spawn <ASSIGNMENT>`, which
does all of the launch wiring below for you. Reach for the manual recipe when you
are launching or forking a session outside that path: resuming a compacted
conversation, re-driving a single step, or running a session that is not tied to
a spawnable Assignment.

These flags and file paths are a snapshot of host behaviour, and the spawn
machinery that exercises them changes. Where it matters, this page states the
*contract* (what has to be true) over the current file layout, so it survives a
relocation of, say, where a prompt file gets written.

## Launching or forking a Bob into a window

`workmux add <name> ...` cuts a git worktree and a tmux window and starts an agent
in it. The pieces that make that agent a *resumed, trusting, correctly-pointed*
Bob rather than a cold shell:

### Fork an existing conversation

```
workmux add <name> --fork=<session-id>
```

forks a conversation into the new window's Claude session: the new session
resumes from the one named. Omit the id (`--fork` alone) to fork the most recent
conversation in the current worktree. This is how a fresh window inherits a
primed Foundation, or picks a compacted session back up, instead of starting from
nothing.

The fork resolves its *source* conversation from the window's working directory.
Claude Code stores each session at:

```
$CLAUDE_CONFIG_DIR/projects/<encoded-cwd>/<session-id>.jsonl
```

where `<encoded-cwd>` is the session's absolute working directory with **every
non-alphanumeric character replaced by a hyphen, one-to-one**: no run-collapsing,
so `/root/repo__worktrees/bob-7` becomes `-root-repo--worktrees-bob-7`. For a fork
to resolve, the source `<session-id>.jsonl` must already be present in the project
directory encoded from the cwd the agent runs in. If it is not there, copy it in
before the `workmux add`.

### Supply the agent command explicitly

workmux runs whatever you hand it via `--agent "<command>"`; it does **not**
auto-detect `claude`. Pass the full invocation. For an autonomous Bob that is the
`claude` binary in auto permission mode:

```
--agent "<env trio> /usr/bin/claude --permission-mode auto ..."
```

### Bake the environment trio onto the command line

A tmux window inherits the **tmux server's** environment, not the environment of
the shell that ran `workmux add`. So the three values a Bob needs must be set *on
the agent command itself* (an env prefix, as above), never merely exported in your
shell:

- `CLAUDE_CONFIG_DIR`: where `claude --resume` finds the session transcript, and
  where it loads skills and hooks from.
- `VV_DATA_DIR`: where `vv` reads and writes its data (Foundation state, the
  project map).
- `PATH`: which `vv`, `claude`, and the helper binaries resolve to.

Omit one and nothing errors: the Bob silently runs against whatever the host
install provides. That is the wrong target, reported as success: the failure mode
to watch for.

### Inject the first turn

```
--prompt-file <path>
```

hands the agent its opening user message; workmux reads the file and injects it as
the first turn (use `--prompt "<text>"` for a short inline body). This is the Bob's
Brief, or whatever instruction it should wake up on.

### Pre-accept folder trust

The first time Claude Code opens a directory it does not recognize, it blocks on an
interactive "trust this folder?" dialog. A headless / remote-control Bob has no one
to answer it and hangs before it reads its first turn. Pre-write the trust flag for
the worktree path, under `projects` in `$CLAUDE_CONFIG_DIR/.claude.json` (or
`~/.claude.json` on the host install):

```json
{ "projects": { "<absolute-worktree-path>": { "hasTrustDialogAccepted": true } } }
```

Launching a Bob into a worktree *is* the act of trusting that worktree, so writing
the flag is recording a decision already made, not bypassing a safeguard.

## Driving a running Bob

### Send input with `workmux send`, not `tmux send-keys`

```
workmux send <name> "<text>"
```

is the reliable keyboard stand-in. Claude Code's TUI does not reliably accept input
from `tmux send-keys`; `workmux send` writes through cleanly. Use it for everything
you would type, including slash commands: `workmux send <name> "/realize"`.

### Read the transcript, not the pane

The Bob's **transcript** (the `<session-id>.jsonl` under `projects/<encoded-cwd>/`)
is the source of truth for what it actually said and did. Do not rely on
`tmux capture-pane`: the pane is a display surface and shows
autocomplete-suggestion text sitting in the input box that nobody typed. Grep the
transcript to observe a tool call, a skill firing, or a message arriving.

### Wait with a foreground poll

To wait for a Bob to reach a state (a check-in arriving, a PR opening, CI going
green) use a foreground poll in a single call:

```
until <condition>; do sleep N; done
```

Backgrounded work and its notifications do not reliably arrive; a foreground
`until` exits exactly when the condition becomes true.

