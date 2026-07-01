from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import assert_never

# Codex's login is not literally "codex" but carries it ("chatgpt-codex-connector[bot]").
_REVIEWER = "codex"

# A +1 carries no commit, so its currency on a head is a question of precedence against the
# moment the head came under watch. The +1's stamp is GitHub's clock and the head's is ours, so
# a +1 must clear the head stamp by more than the plausible skew between them to count current.
# Erring toward not-current only costs a wait, never an early convergence — the head-anchored
# Findings check blocks that independently — so the margin is set generously.
_SIGNOFF_SKEW_SECONDS = 120.0

JsonObject = Mapping[str, object]


@dataclass(frozen=True)
class Findings:
    """The reviewer posted a review anchored to the current head: it has findings on this code."""


@dataclass(frozen=True)
class Clean:
    """The reviewer left a +1 and no review on the head; `at` is its GitHub-clock epoch."""

    at: float


@dataclass(frozen=True)
class Silence:
    """The reviewer has left no signal on the current head."""


# The reviewer's signal on the current head, total over the three things it can be. A review and
# a +1 cannot both be the signal: a review on the head dominates, because a +1 cannot un-say a
# finding. Currency of the +1 is not resolved here — that needs the head clock — so Clean carries
# the raw stamp and the resolution is `disposition`'s.
ReviewerSignal = Findings | Clean | Silence


class ReviewDisposition(Enum):
    CLEAN = "clean"
    FINDINGS = "findings"
    PENDING = "pending"


def login(item: JsonObject) -> str:
    user = item.get("user")
    return str(user.get("login", "")) if isinstance(user, Mapping) else ""


def is_reviewer(login: str) -> bool:
    return _REVIEWER in login.lower()


def reviewer_signal(
    reviews: Sequence[JsonObject],
    reactions: Sequence[JsonObject],
    head_sha: str,
) -> ReviewerSignal:
    if _reviewed_head(reviews, head_sha):
        return Findings()
    signoff = _latest_signoff(reactions)
    return Clean(at=signoff) if signoff is not None else Silence()


def disposition(signal: ReviewerSignal, *, head_first_seen_at: float) -> ReviewDisposition:
    # The reviewer's disposition toward this head, resolving the +1's currency against the head
    # clock so the decision downstream reads a head-relative verdict, never a raw timestamp. A +1
    # that does not clear the head stamp by the skew margin reads PENDING: the loop waits it out
    # rather than converging on a sign-off that may pre-date the head.
    match signal:
        case Findings():
            return ReviewDisposition.FINDINGS
        case Clean(at=at):
            if at > head_first_seen_at + _SIGNOFF_SKEW_SECONDS:
                return ReviewDisposition.CLEAN
            return ReviewDisposition.PENDING
        case Silence():
            return ReviewDisposition.PENDING
    assert_never(signal)


def _reviewed_head(reviews: Sequence[JsonObject], head_sha: str) -> bool:
    return any(
        is_reviewer(login(review)) and str(review.get("commit_id", "")) == head_sha
        for review in reviews
    )


def _latest_signoff(reactions: Sequence[JsonObject]) -> float | None:
    stamps = [
        _to_epoch(str(reaction.get("created_at", "")))
        for reaction in reactions
        if is_reviewer(login(reaction)) and reaction.get("content") == "+1"
    ]
    return max(stamps) if stamps else None


def _to_epoch(iso8601: str) -> float:
    # GitHub stamps reactions in UTC with a trailing "Z", which fromisoformat reads as "+00:00".
    return datetime.fromisoformat(iso8601.replace("Z", "+00:00")).timestamp()
