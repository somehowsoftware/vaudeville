from __future__ import annotations

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from vaudeville_core import Assignment, AssignmentRef, Comment


def _template_environment(package_path: str) -> Environment:
    return Environment(
        loader=PackageLoader("vaudeville_cue", package_path),
        autoescape=select_autoescape(disabled_extensions=("jinja",), default=False),
        keep_trailing_newline=True,
        undefined=StrictUndefined,
    )


# First-turn rendering dispatches on Assignment kind. Three kinds (Command, Direction, Manual)
# select their template by kind from the kind loader. Only a Premise routes: it carries no kind
# template and falls through to the Route lookup, which forms `{route}.jinja` from the tracker's
# Route value. Any other `type` value is an unrecognized kind and fails loud, so a kind cue has no
# template for (a new kernel kind, or one misspelled past preflight) can never silently render a
# Premise's Route brief. The two loaders are split so the Route lookup sees only the Route
# templates: a stray or invalid Route can resolve to a Premise Route template or fail loud, but
# never to a kind turn.
_route_environment = _template_environment("templates")
_kind_environment = _template_environment("kind_templates")

# A kind here renders its own first turn, selected by kind, outside the Route namespace; a Premise
# is absent because it renders by Route instead.
_KIND_TEMPLATES = {
    "Command": "execute.jinja",
    "Direction": "direction.jinja",
    "Manual": "manual.jinja",
}

# Only a Command reads a Route gloss, and a Command's Route is check-in or direct: the two its kind
# permits. The gloss modulates the execute turn; it never selects the template.
_ROUTE_GLOSSES = {
    "direct": "the work is mechanical and CI-gated and commences without a check-in",
    "check-in": (
        "there may be something about the *what* to clear up with the operator "
        "before you realize it"
    ),
}


def render(assignment: Assignment) -> str:
    if assignment.type in _KIND_TEMPLATES:
        template = _kind_environment.get_template(_KIND_TEMPLATES[assignment.type])
    elif assignment.type == "Premise":
        template = _route_environment.get_template(f"{assignment.route}.jinja")
    else:
        raise ValueError(
            f"first-turn rendering received an unrecognized Assignment kind {assignment.type!r}; "
            f"expected 'Premise' or one of {sorted(_KIND_TEMPLATES)}"
        )
    return template.render(
        assignment_id=assignment.id,
        summary=assignment.summary,
        description=assignment.description,
        discussion=_discussion(assignment.comments),
        dependencies=_dependencies(assignment),
        command_route_gloss=_command_route_gloss(assignment),
        command_check_in=assignment.type == "Command" and assignment.route == "check-in",
        signed_off=assignment.signed_off,
    )


def _command_route_gloss(assignment: Assignment) -> str:
    if assignment.type != "Command":
        return ""
    gloss = _ROUTE_GLOSSES.get(assignment.route)
    if gloss is None:
        return ""
    return f"This was filed under the `{assignment.route}` route, which means {gloss}.\n\n"


# A loadable template here would join render()'s route-lookup namespace, where a non-Route
# route value could resolve to it; composing the section in code keeps that namespace Route-only.
def _discussion(comments: tuple[Comment, ...]) -> str:
    if not comments:
        return ""
    entries = "\n".join(f"**{comment.author}:**\n\n{comment.text}\n" for comment in comments)
    return f"## Discussion\n\n{entries}\n"


# Dependency breadcrumbs: the dep edges vaudeville-core already carries on the assignment,
# surfaced so a Bob can read the graph both ways for the why. Ids and open/resolved state only;
# render() makes no tracker call, so it has no titles. `deps_inward` is what this depends on (per
# vaudeville-core's own spawnability predicate, "every assignment this one depends on");
# `deps_outward` is what depends on it.
def _dependencies(assignment: Assignment) -> str:
    sections = [
        block
        for heading, refs in (
            ("Depends on (the work this builds on)", assignment.deps_inward),
            ("Depended on by (the work that builds on this)", assignment.deps_outward),
        )
        if (block := _dependency_block(heading, refs))
    ]
    if not sections:
        return ""
    return "## Dependencies\n\n" + "\n".join(sections) + "\n"


def _dependency_block(heading: str, refs: tuple[AssignmentRef, ...]) -> str:
    if not refs:
        return ""
    lines = "\n".join(
        f"- {ref.id} ({'resolved' if ref.state_resolved else 'open'})" for ref in refs
    )
    return f"{heading}:\n{lines}\n"
