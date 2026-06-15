"""Shared kernel for Vaudeville subsystems.

`vaudeville-core` is the anti-corruption layer over the YouTrack
backend: it speaks Vaudeville primitives (`Premise`, `Workflow`,
`State`, `Type`, `Route`, `Project`, `Depend`, `Subtask`) and hides
everything YouTrack-shaped.

The package is split by responsibility: ``premises`` owns the value
type and pure helpers, ``queries`` owns read paths, ``mutations``
owns write paths. Consumers import from the package root; the
re-exports below are the contract.
"""

from importlib.metadata import PackageNotFoundError, version

from vaudeville_core.bookkeeping import apply_bookkeeping, apply_transition
from vaudeville_core.config_file import (
    downstream_command,
    list_projects,
    managed_repository_for_project,
    project_from_name,
    project_from_premise_id,
    repo_descriptions,
)
from vaudeville_core.current_reading import current_reading_of_project
from vaudeville_core.mutations import (
    add_comment,
    add_depend,
    attach_subtask,
    claim_premise,
    create_premise,
    remove_depend,
)
from vaudeville_core.predicates import (
    Predicate,
    apply_predicates,
    deps_satisfied,
)
from vaudeville_core.premises import Comment, Premise, PremiseRef, make_premise, sort_key
from vaudeville_core.profiles import ABANDONED, DELIVERED, RETURNED, UNCLAIM, ExitProfile
from vaudeville_core.queries import find_premises, get_premise
from vaudeville_core.worktree import project_from_cwd

try:
    __version__ = version("vaudeville-core")
except PackageNotFoundError:
    __version__ = "0.0.0+source"

__all__ = [
    "ABANDONED",
    "DELIVERED",
    "ExitProfile",
    "Predicate",
    "RETURNED",
    "UNCLAIM",
    "Comment",
    "Premise",
    "PremiseRef",
    "__version__",
    "add_comment",
    "add_depend",
    "apply_bookkeeping",
    "apply_predicates",
    "apply_transition",
    "attach_subtask",
    "claim_premise",
    "create_premise",
    "current_reading_of_project",
    "deps_satisfied",
    "downstream_command",
    "find_premises",
    "get_premise",
    "list_projects",
    "managed_repository_for_project",
    "make_premise",
    "project_from_cwd",
    "project_from_name",
    "project_from_premise_id",
    "remove_depend",
    "repo_descriptions",
    "sort_key",
]
