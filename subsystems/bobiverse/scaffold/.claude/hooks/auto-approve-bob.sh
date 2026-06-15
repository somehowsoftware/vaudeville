#!/bin/bash
# Auto-accept Claude Code's hardcoded `.claude/`-edit guardrail prompt
# in autonomous Bob sessions. Picks option 2 ("Yes, and allow Claude
# to edit its own settings for this session"), which grants session-
# wide approval covering every `.claude/` path.
#
# Gated on CLAUDE_AUTONOMOUS=1 (set by .workmux.yaml when spawning a
# Bob) so it never fires for an operator's interactive sessions.
# Only matches the specific guardrail prompt by its signature line;
# any other prompt that reaches this hook is left alone.

cat > /dev/null  # drain hook payload from stdin

[[ -n "$CLAUDE_AUTONOMOUS" ]] || exit 0
[[ -n "$TMUX_PANE" ]] || exit 0

sleep 0.4  # let the prompt finish rendering

if tmux capture-pane -t "$TMUX_PANE" -p 2>/dev/null \
   | grep -q "allow Claude to edit its own settings for this session"; then
    tmux send-keys -t "$TMUX_PANE" 2 Enter
fi

exit 0
