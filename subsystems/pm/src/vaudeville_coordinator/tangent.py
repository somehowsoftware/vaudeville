"""Compose the body of a tangent Premise from captured fields.

A tangent is a side-concern the operator sets aside without working it out.
Because there is nothing yet to author, only to capture, this module lays
the operator's verbatim prompt and the possibly-relevant context into a
fixed provisional shape, with no composition discretion. The captured fields
are the fixed source every other field is checked against, so anything the
prompt and the code do not support is visibly unsupported.

The captured fields are quoted as blockquotes rather than inlined. An
operator's prompt may itself contain markdown headings or bullets (an
`## Acceptance criteria` section, say) and inlining would let that captured
text masquerade as authored Premise structure, both to a human reader and to
``absorbed.py``, whose acceptance-criteria scan is a line-anchored regex that
would otherwise match a captured heading and report drift on a provisional
tangent. (A code fence would not help: that scan reads raw text, so a heading
inside a fence still matches.) Quoting prefixes every captured line, so no
captured line is read as an authored heading or bullet, while the operator's
words stay faithfully present and attributed.

The fixed form admits no remedy, acceptance criterion, or successor
instruction of its own; prescriptive content has no place to go.
"""

from __future__ import annotations

_PROVISIONAL_BANNER = (
    "> **Tangent, provisional capture.** Filed via `vv tangent` to get a side-concern "
    "off the operator's plate without working it out. Treat every line below as "
    "provisional: this is a captured situation, not a worked-out direction. The verbatim "
    "prompt is the fixed source of truth; check the summary, the context, and anything "
    "you infer against it, and treat whatever the prompt and the code do not support as "
    "unsupported. There is deliberately no remedy, acceptance criterion, or successor "
    "instruction here."
)


def _quoted(captured: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in captured.split("\n"))


def compose_body(prompt: str, context: str) -> str:
    return (
        f"{_PROVISIONAL_BANNER}\n\n"
        f"## Verbatim prompt\n\n{_quoted(prompt)}\n\n"
        f"## Possibly-relevant context\n\n{_quoted(context)}\n"
    )
