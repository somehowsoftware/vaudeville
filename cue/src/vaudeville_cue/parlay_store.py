from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from vaudeville_cue.parlay_tally import Tally

_PARLAY_DIRNAME = "parlay"


@dataclass(frozen=True)
class ParlayLayout:
    state: Path
    # Two faces of the open-comment queue: a rendered file the agent triages from, and a structural
    # file parlay-record reads to route each reply to the right endpoint. Both empty as comments are
    # disposed, because triage acts only on what is still open.
    open_comments: Path
    open_data: Path
    # The full run's reviewer comments, verbatim and cumulative — every round's, not just what is
    # still open. The open queue is the wrong substrate for the repeated-symptom escalation, which
    # convenes on the repetition across rounds: by the time the third round trips, the earlier
    # rounds' findings have been disposed out of the queue, so the committee would be shown the
    # symptoms minus the ones that justified the stop. The rendered file is what the committee
    # reads; the structural sibling is what each sense reads to accumulate onto rather than
    # overwrite, so a finding the poll later drops is not lost.
    history: Path
    history_data: Path


def parlay_layout(scratch_root: Path, repo: str, pr: int) -> ParlayLayout:
    # Keyed by the PR's full identity (owner/repo and number), not number alone: peer repos that
    # converge through one scratch dir can share a PR number, and would otherwise read each
    # other's ledger.
    home = scratch_root / _PARLAY_DIRNAME / repo / str(pr)
    return ParlayLayout(
        state=home / "state.json",
        open_comments=home / "open-comments.md",
        open_data=home / "open-comments.json",
        history=home / "comment-history.md",
        history_data=home / "comment-history.json",
    )


@dataclass(frozen=True)
class Answer:
    comment_id: int
    sha: str


@dataclass(frozen=True)
class RoundState:
    # seen lives apart from the tally's dispositions so the new-comment delta and the ledger cannot
    # drift together. head is the PR head at the last observe. head_first_seen_at is when the loop
    # first watched this head (epoch seconds), the clock every head-relative judgement is measured
    # against.
    tally: Tally
    seen: frozenset[int]
    head: str
    head_first_seen_at: float | None = None
    answers: frozenset[Answer] = frozenset()

    @classmethod
    def fresh(cls) -> RoundState:
        return cls(tally=Tally.empty(), seen=frozenset(), head="", head_first_seen_at=None)


def head_stamp(state: RoundState, *, head: str, moment: float) -> float:
    # The head-currency clock, stamped on a head move (the first head a fresh ledger sees included)
    # and on a ledger that predates the field, so an old commit gets a full window from now rather
    # than one already spent — erring toward waiting, never toward converging early.
    if state.head != head or state.head_first_seen_at is None:
        return moment
    return state.head_first_seen_at


def serialize_state(state: RoundState) -> str:
    return (
        json.dumps(
            {
                "rounds": state.tally.rounds,
                "passes": state.tally.passes,
                "addressed": sorted(state.tally.addressed),
                "open": sorted(state.tally.open),
                "waived_at": state.tally.waived_at,
                "seen": sorted(state.seen),
                "head": state.head,
                "head_first_seen_at": state.head_first_seen_at,
                "answers": [
                    {"comment_id": answer.comment_id, "sha": answer.sha}
                    for answer in sorted(state.answers, key=lambda a: (a.comment_id, a.sha))
                ],
            },
            indent=2,
        )
        + "\n"
    )


def deserialize_state(stored: str) -> RoundState:
    # waived_at, head_first_seen_at, and answers are absent from ledgers written before them, so
    # they read through .get where the always-present counts index directly. A parlay already in
    # flight survives the upgrade, reading as unwaived, unstamped, and with no answers recorded.
    data = json.loads(stored)
    waived_at = data.get("waived_at")
    head_first_seen_at = data.get("head_first_seen_at")
    return RoundState(
        tally=Tally(
            rounds=int(data["rounds"]),
            passes=int(data["passes"]),
            addressed=frozenset(int(comment_id) for comment_id in data["addressed"]),
            open=frozenset(int(comment_id) for comment_id in data["open"]),
            waived_at=None if waived_at is None else int(waived_at),
        ),
        seen=frozenset(int(comment_id) for comment_id in data["seen"]),
        head=str(data["head"]),
        head_first_seen_at=None if head_first_seen_at is None else float(head_first_seen_at),
        answers=frozenset(
            Answer(comment_id=int(answer["comment_id"]), sha=str(answer["sha"]))
            for answer in data.get("answers", [])
        ),
    )


def read_state(path: Path) -> RoundState:
    if not path.is_file():
        return RoundState.fresh()
    return deserialize_state(path.read_text(encoding="utf-8"))


def write_state(path: Path, state: RoundState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_state(state), encoding="utf-8")
