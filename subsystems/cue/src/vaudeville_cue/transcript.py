from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Text:
    text: str


@dataclass(frozen=True)
class ToolUse:
    id: str
    name: str
    file_path: str


@dataclass(frozen=True)
class ToolResult:
    tool_use_id: str
    text: str


Block = Text | ToolUse | ToolResult


@dataclass(frozen=True)
class Message:
    line: int
    role: str
    parent_uuid: str
    timestamp: str
    blocks: tuple[Block, ...]
    prompt_source: str

    @property
    def spoken_text(self) -> str:
        return "\n".join(block.text for block in self.blocks if isinstance(block, Text)).strip()


def messages_from_transcript_lines(lines: Iterable[str]) -> list[Message]:
    messages: list[Message] = []
    for line_number, line in enumerate(lines, start=1):
        record = _record(line)
        if record is None:
            continue
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        messages.append(
            Message(
                line=line_number,
                role=str(message.get("role", "")),
                parent_uuid=str(record.get("parentUuid") or ""),
                timestamp=str(record.get("timestamp") or "")[:19],
                blocks=tuple(_blocks(message.get("content"))),
                # The harness's own provenance for a user record: "typed"/"queued" is
                # the operator speaking; "system"/"sdk" and the absent source are
                # machinery it injects under the user role.
                prompt_source=str(record.get("promptSource") or ""),
            )
        )
    return messages


def _record(line: str) -> dict[str, object] | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        record = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return record if isinstance(record, dict) else None


def _blocks(content: object) -> Iterator[Block]:
    if isinstance(content, str):
        yield Text(content)
        return
    if not isinstance(content, list):
        return
    for block in content:
        if not isinstance(block, dict):
            continue
        kind = block.get("type")
        if kind == "text":
            yield Text(str(block.get("text", "")))
        elif kind == "tool_use":
            input_fields = block.get("input")
            file_path = input_fields.get("file_path", "") if isinstance(input_fields, dict) else ""
            yield ToolUse(
                id=str(block.get("id", "")),
                name=str(block.get("name", "")),
                file_path=str(file_path),
            )
        elif kind == "tool_result":
            yield ToolResult(
                tool_use_id=str(block.get("tool_use_id", "")),
                text=_tool_result_text(block.get("content")),
            )


def _tool_result_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            str(item.get("text", ""))
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""
