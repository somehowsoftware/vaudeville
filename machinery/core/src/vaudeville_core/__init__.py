"""Anti-corruption layer between Vaudeville and the foreign systems it
runs against: the project tracker, git hosting, and the host config.

It speaks Vaudeville primitives (`Assignment`, `Workflow`, `State`,
`Type`, `Route`, `Component`, `Depend`, `Subtask`) and hides everything
the foreign systems are shaped like. Consumers import from the package
root; the re-exports below are the contract.
"""

from importlib.metadata import PackageNotFoundError, version

from vaudeville_core.assignments import (
    Assignment,
    AssignmentRef,
    Comment,
    make_assignment,
    sort_key,
)
from vaudeville_core.bookkeeping import apply_bookkeeping, apply_transition
from vaudeville_core.config_file import (
    component_from_assignment_id,
    component_from_name,
    component_from_prefix,
    downstream_command,
    list_components,
    repo_descriptions,
)
from vaudeville_core.current_reading import current_reading_of_component
from vaudeville_core.mutations import (
    add_comment,
    add_depend,
    attach_subtask,
    claim_assignment,
    create_assignment,
    remove_depend,
    sign_off,
)
from vaudeville_core.predicates import (
    Predicate,
    apply_predicates,
    deps_satisfied,
)
from vaudeville_core.profiles import ABANDONED, DELIVERED, RETURNED, UNCLAIM, ExitProfile
from vaudeville_core.queries import find_assignments, get_assignment
from vaudeville_core.route_constraint import PERMITTED_ROUTES, route_permitted
from vaudeville_core.worktree import component_from_cwd

try:
    __version__ = version("vaudeville-core")
except PackageNotFoundError:
    __version__ = "0.0.0+source"

__all__ = [
    "ABANDONED",
    "DELIVERED",
    "ExitProfile",
    "PERMITTED_ROUTES",
    "Predicate",
    "RETURNED",
    "UNCLAIM",
    "Comment",
    "Assignment",
    "AssignmentRef",
    "__version__",
    "add_comment",
    "add_depend",
    "apply_bookkeeping",
    "apply_predicates",
    "apply_transition",
    "attach_subtask",
    "claim_assignment",
    "create_assignment",
    "current_reading_of_component",
    "deps_satisfied",
    "downstream_command",
    "find_assignments",
    "get_assignment",
    "list_components",
    "component_from_prefix",
    "make_assignment",
    "component_from_cwd",
    "component_from_name",
    "component_from_assignment_id",
    "remove_depend",
    "repo_descriptions",
    "route_permitted",
    "sign_off",
    "sort_key",
]
