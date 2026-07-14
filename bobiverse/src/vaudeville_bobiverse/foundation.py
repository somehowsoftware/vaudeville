from __future__ import annotations

import os
import sys
import tempfile
import threading
import tomllib
from pathlib import Path
from typing import NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

FOUNDATIONS_FILENAME = "foundations.toml"

# The store sits beside the registry: `foundations.toml` indexes prefix →
# session id; `foundations/` holds each session's transcript, addressed by
# session id and independent of any clone path.
TRANSCRIPT_STORE_DIRNAME = "foundations"

# A parallel `vv-bob prime` run saves several Foundations concurrently.
_save_lock = threading.Lock()


class MalformedFoundations(ValueError):
    pass


class _Foundations(BaseModel):
    model_config = ConfigDict(extra="ignore")

    foundations: dict[str, str] = Field(default_factory=dict)


def foundations_from_toml(text: str) -> dict[str, str]:
    try:
        raw = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise MalformedFoundations(str(exc)) from exc
    try:
        return dict(_Foundations.model_validate(raw).foundations)
    except ValidationError as exc:
        raise MalformedFoundations(str(exc)) from exc


def with_foundation(existing: dict[str, str], prefix: str, session_id: str) -> dict[str, str]:
    return {**existing, prefix: session_id}


def foundations_to_toml(registry: dict[str, str]) -> str:
    lines = ["[foundations]"]
    for prefix in sorted(registry):
        lines.append(f'{prefix} = "{registry[prefix]}"')
    return "\n".join(lines) + "\n"


def lookup(prefix: str, *, data_files_root: Path) -> str | None:
    return _read_registry(data_files_root / FOUNDATIONS_FILENAME).get(prefix)


def all_foundations(*, data_files_root: Path) -> dict[str, str]:
    return _read_registry(data_files_root / FOUNDATIONS_FILENAME)


def save(prefix: str, session_id: str, *, data_files_root: Path) -> None:
    with _save_lock:
        path = data_files_root / FOUNDATIONS_FILENAME
        _write(path, with_foundation(_read_registry(path), prefix, session_id))


def transcript_store(*, data_files_root: Path) -> Path:
    return data_files_root / TRANSCRIPT_STORE_DIRNAME


def stored_transcript(session_id: str, *, data_files_root: Path) -> Path:
    return transcript_store(data_files_root=data_files_root) / f"{session_id}.jsonl"


def stored_session_ids(store: Path) -> set[str]:
    if not store.is_dir():
        return set()
    return {transcript.stem for transcript in store.glob("*.jsonl")}


def _read_registry(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        return foundations_from_toml(path.read_text())
    except MalformedFoundations as exc:
        _abort(f"{path} is malformed: {exc}")


def _write(path: Path, registry: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Stage the registry in a sibling temp file and swap it in with an atomic rename, so a
    # kill mid-write leaves the prior file whole rather than a truncation that aborts every
    # later read. The temp shares the registry's directory because os.replace is atomic only
    # within one filesystem; no fsync, since the threat is a process kill (whose page cache
    # survives), not power loss.
    #
    # Sweep any temp an earlier write orphaned before staging a new one. That kill lands out
    # of frame — a prime fork saves in a ThreadPoolExecutor worker, and a hung process takes
    # SIGKILL — so the finally below runs only for a catchable in-thread failure, never for
    # the kill this fix exists to survive. Under a kill the temp is left behind, and mkstemp
    # mints a fresh name each time, so without this sweep every interrupted prime would strand
    # another one to accumulate unbounded. The sweep runs under the _save_lock that save
    # holds, so it never removes a temp another thread has in flight.
    for orphan in path.parent.glob(f"{path.name}.*.tmp"):
        orphan.unlink(missing_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as staged:
            staged.write(foundations_to_toml(registry))
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _abort(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)
