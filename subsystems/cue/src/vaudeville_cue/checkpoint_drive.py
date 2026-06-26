from __future__ import annotations

import os
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import NoReturn

_CLEAR_TIMEOUT_ENV = "CHECKPOINT_CLEAR_TIMEOUT"
_POLL_INTERVAL_ENV = "CHECKPOINT_CLEAR_POLL_INTERVAL"
_GATE_TIMEOUT_ENV = "CHECKPOINT_GATE_TIMEOUT"
_APPEARANCE_TIMEOUT_ENV = "CHECKPOINT_APPEARANCE_TIMEOUT"


def session_transcripts(transcript_dir: Path) -> frozenset[str]:
    # A session's id is the stem of its <id>.jsonl spine.
    return frozenset(spine.stem for spine in transcript_dir.glob("*.jsonl"))


def new_sessions(baseline: frozenset[str], current: frozenset[str]) -> frozenset[str]:
    return current - baseline


class LostClearCause(Enum):
    # The pane never reached idle within the budget, so /clear was never sent.
    PANE_NEVER_SETTLED = "pane-never-settled"
    # /clear was sent, but no successor session ever appeared to inject into.
    CLEARED_SESSION_NEVER_APPEARED = "cleared-session-never-appeared"


_LOST_CLEAR_NOTICE = """\
# The /clear was lost; you are still in your pre-checkpoint session

{detail}

You were not cleared. You are still live in the conversation you were in when you
ran `vv checkpoint`: nothing was shed, and the Resume Brief was never injected as
a freshly-cleared session's first turn.

Your Digest, Carryover, and composed Resume Brief are already persisted under
{scratch_dir}; nothing was lost, only the clear itself failed.

Recovery is this conversation's call, not an automatic retry. Decide with the
operator whether to re-checkpoint.
"""

_CAUSE_DETAIL = {
    LostClearCause.PANE_NEVER_SETTLED: (
        "The pane never settled to idle within the gate window, so `/clear` was never even "
        "sent. This usually means output was produced after the `vv checkpoint` call; the "
        "checkpoint turn must end at that call and produce nothing after it."
    ),
    LostClearCause.CLEARED_SESSION_NEVER_APPEARED: (
        "`/clear` was sent, but no freshly-cleared session ever appeared within the timeout, "
        "so the Resume Brief was never injected."
    ),
}


def lost_clear_notice(cause: LostClearCause, scratch_dir: Path) -> str:
    # The mirror of the Resume Brief: composed pure here, sent by the shell. Where the Brief
    # is the first turn of a session that cleared, this is the turn a Bob reads in the session
    # that did not: it names the strand, the surviving artifacts, and whose call recovery is.
    return _LOST_CLEAR_NOTICE.format(detail=_CAUSE_DETAIL[cause], scratch_dir=scratch_dir)


def _strand(pane: str, cause: LostClearCause, scratch_dir: Path) -> NoReturn:
    # The clear was lost, so the resumed session that would have read a Brief never exists; the
    # only reader left is the still-live Bob in its pane. Signal it there, then exit nonzero into
    # the drive log as the terminus. The send is check=True: if even that fails there is nothing
    # left to try, and its error is the last thing the log records.
    subprocess.run(  # noqa: S603, S607
        ["workmux", "send", pane, lost_clear_notice(cause, scratch_dir)], check=True
    )
    sys.exit(
        f"Error: {cause.value}; stranded '{pane}' in its pre-checkpoint session "
        "and signalled the strand to that pane."
    )


def _land_clear(
    pane: str,
    transcript_dir: Path,
    pre_existing: frozenset[str],
    *,
    gate_timeout: str,
    appearance_timeout: float,
    poll_interval: float,
) -> LostClearCause | None:
    # The gate runs every round, never trusted from a stale settle: a /clear sent into a busy
    # pane is absorbed as buffered input rather than run, so we send only into a pane workmux
    # confirms idle right now. A pane that settles, swallows a /clear, then re-busies is gated
    # afresh before the next send.
    settled = subprocess.run(  # noqa: S603, S607
        ["workmux", "wait", "--status", "done", "--timeout", gate_timeout, pane], check=False
    )
    if settled.returncode != 0:
        return LostClearCause.PANE_NEVER_SETTLED
    # Check before sending: a successor from a clear applied on an earlier round may already be
    # present. Identity is monotone: once any successor exists the clear has taken effect, so a
    # second /clear here would needlessly re-clear a session that already cleared. Testing the
    # single baseline (never a per-round one) is what carries that recognition across rounds.
    if new_sessions(pre_existing, session_transcripts(transcript_dir)):
        return None
    subprocess.run(["workmux", "send", pane, "/clear"], check=True)  # noqa: S603, S607
    # The appearance window opens here, at the send, not at the round's start. The gate above
    # can spend real time waiting for a re-busied pane to settle, so a window anchored before it
    # could be wholly spent by the time /clear is sent, stranding a pane whose clear had just
    # taken effect. It is also uncapped by the overall deadline: once the destructive /clear is
    # sent, the successor it may have just spawned is owed a full window to surface, even a little
    # past the deadline. The deadline bounds whether drive() opens another round, not how long we
    # watch the result of a send already made.
    appearance_deadline = time.monotonic() + appearance_timeout
    while not new_sessions(pre_existing, session_transcripts(transcript_dir)):
        if time.monotonic() >= appearance_deadline:
            return LostClearCause.CLEARED_SESSION_NEVER_APPEARED
        time.sleep(poll_interval)
    return None


def drive(
    pane: str,
    transcript_dir: Path,
    brief: Path,
    *,
    timeout: float,
    poll_interval: float,
    gate_timeout: str,
    appearance_timeout: float,
) -> None:
    scratch_dir = brief.parent
    # The single baseline: capture the pre-existing session ids once, before any round could send
    # a /clear: the one instant guaranteed to precede every clear this run spawns. Carried
    # unchanged across all rounds, it makes recognition monotone: a successor that appears late on
    # one round is still "new" against this baseline on the next, so a later round recognizes it
    # for free and the check-before-send never re-clears an already-cleared session.
    #
    # Re-baselining per round (after each gate) would fold a late-appearing successor into that
    # round's baseline, forget the appearance it caused, and re-clear an already-cleared session,
    # so the baseline is captured once here, never inside a round. The cost of the single baseline
    # is that a session born concurrently during a gate also reads as "new": an inference a
    # directory census cannot disambiguate from outside workmux. In the one-Bob-per-worktree model
    # there are no concurrent writers, so no such stray arises: the only thing that mints a new id
    # is our own clear. The true confirmation (the new session id echoed back from the send) lives
    # on the workmux side of the boundary and is out of scope.
    pre_existing = session_transcripts(transcript_dir)
    deadline = time.monotonic() + timeout
    # The strand cause records how far the rounds reached. A /clear is only sent from inside a
    # confirmed-idle gate, so until some round settles and sends, the cause stays "never
    # settled"; the first send upgrades it to "never appeared" and it never falls back.
    cause = LostClearCause.PANE_NEVER_SETTLED
    # The deadline is the loop's own condition, so it bounds whether another round opens: a round
    # already in flight finishes past it (the appearance window is owed to a /clear already sent),
    # but no new round, and so no new /clear, starts once the budget is spent. The backoff at the
    # foot of the loop is re-checked here before the next round, so a lost round's sleep cannot
    # carry a fresh round past the deadline.
    while time.monotonic() < deadline:
        lost = _land_clear(
            pane,
            transcript_dir,
            pre_existing,
            gate_timeout=gate_timeout,
            appearance_timeout=appearance_timeout,
            poll_interval=poll_interval,
        )
        if lost is None:
            subprocess.run(  # noqa: S603, S607
                ["workmux", "send", pane, "--file", str(brief)], check=True
            )
            return
        if lost is LostClearCause.CLEARED_SESSION_NEVER_APPEARED:
            cause = lost
        # A lost round normally spends real time (a busy gate consumes its timeout, a sent clear
        # its appearance window), but a gate that fails instantly, such as a bad pane or a workmux
        # command error, spends none; the bare loop would then re-invoke workmux as fast as it can
        # reject the call. Back off by the poll interval so the retry cadence is bounded by the
        # clock, not by workmux's failure speed, while still recovering if a transient gate error
        # clears on a later round.
        time.sleep(poll_interval)
    _strand(pane, cause, scratch_dir)


def main(argv: list[str]) -> None:
    pane, transcript_dir, brief = argv
    drive(
        pane,
        Path(transcript_dir),
        Path(brief),
        timeout=float(os.environ.get(_CLEAR_TIMEOUT_ENV, "300")),
        poll_interval=float(os.environ.get(_POLL_INTERVAL_ENV, "2")),
        gate_timeout=os.environ.get(_GATE_TIMEOUT_ENV, "300"),
        appearance_timeout=float(os.environ.get(_APPEARANCE_TIMEOUT_ENV, "30")),
    )


if __name__ == "__main__":
    main(sys.argv[1:])
