from __future__ import annotations

import json
from collections.abc import Sequence

from vaudeville_cue.digest import OperatorTurn, Section, UnconfirmedQueuedMessage


def serialize_sections(sections: Sequence[Section]) -> str:
    return (
        json.dumps(
            [
                {
                    "source": section.source,
                    "turns": [
                        {
                            "line": turn.line,
                            "timestamp": turn.timestamp,
                            "text": turn.text,
                            "via_tmp": turn.via_tmp,
                        }
                        for turn in section.turns
                    ],
                    "remnants": [
                        {
                            "line": remnant.line,
                            "timestamp": remnant.timestamp,
                            "text": remnant.text,
                        }
                        for remnant in section.remnants
                    ],
                }
                for section in sections
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def deserialize_sections(stored: str) -> tuple[Section, ...]:
    return tuple(
        Section(
            source=str(entry["source"]),
            turns=tuple(
                OperatorTurn(
                    line=int(turn["line"]),
                    timestamp=str(turn["timestamp"]),
                    text=str(turn["text"]),
                    via_tmp=bool(turn["via_tmp"]),
                )
                for turn in entry["turns"]
            ),
            remnants=tuple(
                UnconfirmedQueuedMessage(
                    line=int(remnant["line"]),
                    timestamp=str(remnant["timestamp"]),
                    text=str(remnant["text"]),
                )
                for remnant in entry.get("remnants", [])
            ),
        )
        for entry in json.loads(stored)
    )
