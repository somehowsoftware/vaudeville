"""The host ``vv`` runner: invoke the deployed Composed CLI against the Host, never the rehearsal
scratch. Install runs in the rehearse shell once the smoke clears, so a call inheriting its
Rehearsal Redirect (``CLAUDE_CONFIG_DIR``/``VV_DATA_DIR``) would act on the Rehearsal Installation
and re-create the missing-Foundations failure the post-placement steps exist to prevent.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from vaudeville_install.child_process import Outcome, Spec

REHEARSAL_REDIRECT_ENV_VARS = frozenset({"CLAUDE_CONFIG_DIR", "VV_DATA_DIR"})

RunVv = Callable[[Sequence[str]], Outcome]
# Injected at the composition root so this module spawns nothing.
RunChild = Callable[[Spec], Outcome]


def host_vv_environment(base_env: Mapping[str, str]) -> dict[str, str]:
    # Minus the Rehearsal Redirect, so a host `vv` call runs against the Host's own `~/.claude` and
    # `~/.vaudeville`, never the smoke's scratch. `PATH` and a genuine non-default host config
    # survive: Priming needs the host's `claude`.
    return {
        name: value for name, value in base_env.items() if name not in REHEARSAL_REDIRECT_ENV_VARS
    }


def build_vv_spec(
    vv_path: Path,
    env: Mapping[str, str],
    args: Sequence[str],
    *,
    capture_stdout: bool,
    timeout: float,
) -> Spec:
    return Spec(argv=(str(vv_path), *args), env=env, timeout=timeout, capture_stdout=capture_stdout)


def capturing_vv_runner(
    run_child: RunChild, vv_path: Path, env: Mapping[str, str], timeout: float
) -> RunVv:
    # For probes that parse `vv`'s output (Commissioning): capture stdout so the caller can read it
    # back. stderr is captured either way, by the child-process boundary.
    def run_vv(args: Sequence[str]) -> Outcome:
        return run_child(build_vv_spec(vv_path, env, args, capture_stdout=True, timeout=timeout))

    return run_vv


def streaming_vv_runner(
    run_child: RunChild, vv_path: Path, env: Mapping[str, str], timeout: float
) -> RunVv:
    # For `vv prime`: leave stdout inherited so its live `claude --print` turn reaches the operator,
    # while stderr is captured so a failure's account survives into FoundationsNotPrimed.
    def run_vv(args: Sequence[str]) -> Outcome:
        return run_child(build_vv_spec(vv_path, env, args, capture_stdout=False, timeout=timeout))

    return run_vv
