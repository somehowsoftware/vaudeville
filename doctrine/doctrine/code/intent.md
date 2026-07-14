# Intent

A system's intent (what it is, what it does, how it does it) lives in three places, by layer:

- **The spec** carries the high-level WHAT. One paragraph to one page per Context, at a level that survives many code changes. A spec that churns with every refactor has slipped into territory tests should pin.
- **The tests** carry the low-level WHAT. Each test name states a contract in domain terms; the body proves it.
- **The code** carries the HOW. Literate, in the [ubiquitous language](language.md), with names that hit you over the head. Code is the only place behaviour is described in operational detail.

The ubiquitous language sits alongside as a reference vocabulary: terms defined in relation to one another, distinct from the spec. Cross-context UL lives in [vocabulary](../vocabulary.md); context-local UL lives in each Context's own UL doc, which references the cross-context vocabulary rather than redefining it.

## The repository boundary is the Component boundary

No document marks where one Component ends and another begins: the git repository's filesystem boundary is the marker. For a Context that boundary is also its jurisdiction's edge, where one bounded domain stops and the next begins; a Resource has the same physical boundary with no domain behind it. A `bounded-context.md` (or similar) is a smell: such a file mixes spec, vocabulary, and behaviour description, and rots as the code drifts.

## Doctrine present in the artefact under edit

Each canonical doc shape opens with one sentence stating what kind of doc it is and where its sibling layers live:

- A spec doc opens with: *"This is a spec: high-level WHAT. Low-level WHAT is in the test suite; HOW is in the code."*
- A UL doc opens with: *"This is a UL doc: terms defined in relation to one another. For framework-level UL see `~/.vaudeville/doctrine/vocabulary.md`."*

## What does not get written

Do not write:

- A doc describing rejection conditions, dispatch logic, orchestration shape, or any other behaviour the test suite already pins. That description belongs in the tests.
- A doc walking through an orchestration's modules in prose. The module imports and structure are the description.
- A `bounded-context.md`, `architecture-overview.md`, or similar doc whose content is "what the code does in detail." Such a file invariably drifts.
- Cross-references between docs that double-book what the [vocabulary](../vocabulary.md) entries already define. Define a term once; link to that definition.
- A decision record, ADR, or any persistent doc whose purpose is to preserve the rationale of a past choice. Where the *why* of a non-obvious choice needs to survive, it goes at the action point: a comment in the code or workflow file the choice lives in, the PR description or commit message that introduced it, or a UL entry if the concept is structural enough for vocabulary.

Do write: a short spec when the high-level WHAT earns one (some Contexts do not), a UL doc for context-local terms, and code+tests that explain the system through their own shape. These three are exhaustive of the canonical doc kinds in a repo's persistent layout. Another shape (architecture overview, design doc, decision record, change log) is a finding, not a stylistic choice; before writing one, ask which of the three canonical shapes its content actually belongs in.

## Mechanism

- **Codebase shape teaches by example.** A fresh agent reading a Context inherits the shape of the docs it sees; keep every Context's docs well-organised, because the per-repo priming fanout inherits their shape.
- **Front matter at the top of each canonical shape** surfaces the doctrine at the action point.
- **Review at PR time** is the backstop for cases the prior two miss; not the primary mechanism.

Priming-time and skill-text exhortations are deliberately not the primary mechanism: they are too far from the action point to pull the outcome reliably.
