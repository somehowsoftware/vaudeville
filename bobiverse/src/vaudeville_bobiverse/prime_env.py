from __future__ import annotations


# Priming reads each Component's source by cloning its remote; a private remote
# with no wired credential must make that clone fail at once, never block a
# headless prime on an interactive credential prompt on a tty it happened to
# inherit. These settings make git non-interactive across every transport, so
# "priming never blocks on a human" holds categorically: GIT_TERMINAL_PROMPT=0
# refuses the https username/password prompt, and ssh BatchMode=yes refuses the
# ssh passphrase and unknown-host prompts. An unauthenticated clone then aborts
# rather than hanging.
def noninteractive_git_env() -> dict[str, str]:
    return {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_SSH_COMMAND": "ssh -o BatchMode=yes",
    }
