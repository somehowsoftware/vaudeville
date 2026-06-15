from __future__ import annotations

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from vaudeville_core import Comment, Premise

_environment = Environment(
    loader=PackageLoader("vaudeville_cue", "templates"),
    autoescape=select_autoescape(disabled_extensions=("jinja",), default=False),
    keep_trailing_newline=True,
    undefined=StrictUndefined,
)


def render(premise: Premise) -> str:
    template = _environment.get_template(f"{premise.route}.jinja")
    return template.render(
        premise_id=premise.id,
        summary=premise.summary,
        description=premise.description,
        discussion=_discussion(premise.comments),
    )


# A loadable template here would join render()'s route-lookup namespace, where a non-Route
# route value could resolve to it; composing the section in code keeps that namespace Route-only.
def _discussion(comments: tuple[Comment, ...]) -> str:
    if not comments:
        return ""
    entries = "\n".join(f"**{comment.author}:**\n\n{comment.text}\n" for comment in comments)
    return f"## Discussion\n\n{entries}\n"
