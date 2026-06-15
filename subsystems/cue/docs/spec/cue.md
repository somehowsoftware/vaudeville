*This is a spec — high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code. The doctrine for this layering is in `~/.vaudeville/doctrine/code/intent.md`.*

# vaudeville-cue

vaudeville-cue produces the first-turn body for a freshly-spawned Bob. The /spawn pipeline calls `vv premise-context <PREMISE>` to get that body; this subrepo's job is to render it. Fetch the Premise from the tracker, pick the Jinja template that matches its Route, render the template with the Premise's id, summary, description, and accumulated comment thread, and write the result to stdout.

The templates are doctrine: each one encodes what a first turn for that disposition looks like — `direct` materializes, `check-in` surfaces a decision, `plan` decomposes the work into child Premises, `manual` opens an unbounded conversation. The set of templates IS the set of spawnable Routes; adding a Route to the constellation means adding a template here.

Pickability gating — wrong Type, resolved/claimed Workflow, missing or unknown Route, deps-unresolved, scope — is `vv spawn-preflight`'s job upstream of this subrepo. cue assumes a valid spawnable Premise; if an invalid one reaches it, Jinja raises a loud TemplateNotFound rather than being absorbed by a second taxonomy here.
