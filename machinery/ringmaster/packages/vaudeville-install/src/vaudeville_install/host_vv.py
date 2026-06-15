"""The host ``vv`` runner: invoke the deployed Facade against the Host, never the staged scratch.

Apply's post-install steps — priming the Foundations and the integrity check — are both host ``vv``
calls. They share one runner so the rehearse shell's Staging redirects are stripped in exactly one
place. A rehearse shell exports ``CLAUDE_CONFIG_DIR`` and ``VV_DATA_DIR`` to point the smoke at the
Staged Scaffold, and Apply runs in that same shell once the smoke clears; a host ``vv`` call that
inherited either would act on the staged scratch — forking Foundation transcripts there
(``CLAUDE_CONFIG_DIR``) or reading and writing ``foundations.toml`` there (``VV_DATA_DIR``) — and
re-create the missing-Foundations failure the post-install steps exist to prevent.

``host_vv_environment`` strips both. The composition root resolves it from the operator's real
environment once and injects the runners inward; no operation reaches ``os.environ`` itself, so a
host ``vv`` call against the staged scratch is not something the code can express. ``PATH`` is
kept: priming needs the host's ``claude``, and a runner invokes ``vv`` by absolute path.

Two runner shapes share that environment. The integrity probes parse ``vv``'s output, so they run
through a capturing runner. ``vv prime`` is interactive — it drives Claude and may surface a
first-run auth prompt or a stuck turn — so it runs through a runner that inherits the terminal;
capturing it would hide those prompts behind a pipe and make ``ringmaster apply`` look hung.
"""

from __future__ import annotations

import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

STAGING_REDIRECT_ENV_VARS = frozenset({"CLAUDE_CONFIG_DIR", "VV_DATA_DIR"})


@dataclass(frozen=True)
class VvResult:
    returncode: int
    stdout: str
    stderr: str


class RunVv(Protocol):
    def __call__(self, args: list[str]) -> VvResult: ...


def host_vv_environment(base_env: Mapping[str, str]) -> dict[str, str]:
    # The operator's own environment minus the Staging redirects, so a host `vv` call lands on the
    # Host's `~/.claude` and `~/.vaudeville`, never the smoke's scratch. A genuine non-default host
    # config survives. Resolved at the composition root and injected; see the module docstring.
    return {
        name: value for name, value in base_env.items() if name not in STAGING_REDIRECT_ENV_VARS
    }


def capturing_vv_runner(vv_path: Path, env: Mapping[str, str]) -> RunVv:
    # For probes that parse `vv`'s output (the integrity check): capture stdout/stderr so the caller
    # can read them back.
    return _vv_runner(vv_path, env, capture=True)


def interactive_vv_runner(vv_path: Path, env: Mapping[str, str]) -> RunVv:
    # For the interactive `vv prime`: inherit the terminal so its prompts and streaming progress
    # reach the operator and the operator can respond. Capturing it would hide a first-run auth
    # prompt or a stuck turn behind a pipe and make `ringmaster apply` look hung.
    return _vv_runner(vv_path, env, capture=False)


def _vv_runner(vv_path: Path, env: Mapping[str, str], *, capture: bool) -> RunVv:
    # The imperative shell. `env` is supplied by the composition root (host_vv_environment of the
    # operator's environment) and carries no default here: a runner cannot be built without being
    # told the environment to run in, so a host `vv` call against the staged scratch is unwriteable.
    def run_vv(args: list[str]) -> VvResult:
        try:
            completed = subprocess.run(
                [str(vv_path), *args],
                capture_output=capture,
                text=True,
                check=False,
                env=dict(env),
            )
        except OSError as launch_failure:
            # An absent or non-executable `vv` is itself a missing-dispatcher failure; keep it on
            # the loud-failure path rather than letting OSError escape as a traceback.
            return VvResult(127, "", f"could not launch `vv` at {vv_path}: {launch_failure}")
        # An interactive runner inherits the terminal, so stdout/stderr come back as None.
        return VvResult(completed.returncode, completed.stdout or "", completed.stderr or "")

    return run_vv
