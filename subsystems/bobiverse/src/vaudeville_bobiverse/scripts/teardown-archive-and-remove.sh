#!/usr/bin/env bash
# Archive a worktree's working tree to a timestamped directory under
# $WORKTREE_ARCHIVE_ROOT, then tear down its workmux entry (tmux window +
# git worktree + local branch).
#
# Designed to be launched DETACHED (setsid + nohup + &) from the agent
# whose own tmux pane this script will kill. Once the pane dies the
# agent dies too, so this script must outlive both — that is what the
# detachment buys us. Every `/closeout <disposition>` delegates here
# through `vv teardown`, regardless of disposition.
#
# Usage:
#   setsid nohup bash scripts/teardown-archive-and-remove.sh [name] \
#       >> /tmp/teardown-archive.log 2>&1 < /dev/null &
#
# If [name] is omitted, the worktree name is derived from the basename
# of the invoker's git toplevel (matching workmux's own naming), so the
# script works regardless of which subdirectory of the worktree it is
# launched from.

set -euo pipefail

INVOCATION_PWD="$PWD"

# Resolve the worktree name BEFORE we cd anywhere. When no argument is
# given, derive it from the git toplevel of the invoker's PWD — not from
# PWD itself, so launching from any subdirectory of the worktree still
# resolves to the worktree's root.
if [[ -n "${1:-}" ]]; then
  NAME="$1"
else
  WT_ROOT="$(git -C "$INVOCATION_PWD" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -z "$WT_ROOT" ]]; then
    echo "ERROR: not in a git worktree and no name argument given" >&2
    exit 1
  fi
  NAME="$(basename "$WT_ROOT")"
fi

# Resolve the main worktree (shared git dir's parent) BEFORE we cd anywhere.
# Both `workmux path` and `workmux remove` need a git repo cwd to enumerate
# worktrees — running from `/` fails with "not a git repository". The main
# worktree survives removal of this one, so it's a safe cwd for teardown.
MAIN_REPO="$(dirname "$(git -C "$INVOCATION_PWD" rev-parse --path-format=absolute --git-common-dir)")"

ARCHIVE_ROOT="${WORKTREE_ARCHIVE_ROOT:-/root/vaudeville-bobiverse__worktrees__archive}"

log() { echo "[$(date -Is)] $*"; }

# Resolve the worktree path while we're still inside a git repo.
WT_PATH="$(workmux path "$NAME" 2>/dev/null || true)"
if [[ -z "$WT_PATH" || ! -d "$WT_PATH" ]]; then
  log "ERROR: cannot resolve worktree path for '$NAME'"
  exit 1
fi

# Derive the Claude transcript directory from $WT_PATH using Claude Code's
# project-dir encoding: replace every non-alphanumeric character with '-'. This
# must stay identical to claude_projects.project_directory in Python (the spawn
# seed and prime store use that one); a path with a space or punctuation that
# the two encoded differently would archive from the wrong directory here. A
# missing transcript dir aborts before teardown unless the caller opts out — the
# encoding is load-bearing, so silent data loss on an encoding change would
# be worse than one loud failure on this node.
#
# Claude Code keeps its sessions under $CLAUDE_CONFIG_DIR (default ~/.claude),
# so the transcript root must follow that variable too — a rehearse Session
# points CLAUDE_CONFIG_DIR at the Staged Scaffold, and hardcoding ~/.claude
# would look for the transcript on the host scaffold and abort teardown.
CLAUDE_PROJECTS_ROOT="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
TRANSCRIPT_DIR="$CLAUDE_PROJECTS_ROOT/$(printf '%s' "$WT_PATH" | sed 's/[^A-Za-z0-9]/-/g')"
if [[ -d "$TRANSCRIPT_DIR" ]]; then
  TRANSCRIPT_PRESENT=1
elif [[ "${EXIT_ARCHIVE_ALLOW_NO_TRANSCRIPT:-}" == "1" ]]; then
  log "WARNING: transcript directory $TRANSCRIPT_DIR not found; EXIT_ARCHIVE_ALLOW_NO_TRANSCRIPT=1 set, proceeding"
  TRANSCRIPT_PRESENT=0
else
  log "ERROR: transcript directory $TRANSCRIPT_DIR not found; set EXIT_ARCHIVE_ALLOW_NO_TRANSCRIPT=1 to override"
  exit 1
fi

# Step out of anything we're about to delete, into a cwd where workmux
# remove can still see the shared git dir.
cd "$MAIN_REPO"

mkdir -p "$ARCHIVE_ROOT"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$ARCHIVE_ROOT/${NAME}__${TIMESTAMP}"

log "Archiving $WT_PATH -> $DEST"
rsync -a \
  --exclude='node_modules' \
  --exclude='target' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.next' \
  "$WT_PATH/" "$DEST/"

if [[ "$TRANSCRIPT_PRESENT" == "1" ]]; then
  # Dot-prefixed name reserves the path for archive metadata: a project
  # whose worktree already contains a top-level `transcripts/` directory
  # would otherwise be silently merged with Claude's session files.
  log "Archiving transcripts $TRANSCRIPT_DIR -> $DEST/.claude-transcripts/"
  rsync -a "$TRANSCRIPT_DIR/" "$DEST/.claude-transcripts/"
fi

log "Tearing down workmux entry for '$NAME' (kills pane, removes worktree and branch)"
workmux remove --force "$NAME"
log "Done."
