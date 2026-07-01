# Prose is code

Agent-facing prose — a skill step, a first-turn template, any standing prompt —
invites you to treat it as writing: read it for sense, polish it, keep the version
that reads best. That instinct is wrong here. The prose we feed an agent is not
writing it reads; it is code it runs. An agent is a stochastic interpreter, and a
wording is a program executed against it. This is literal, not a figure of speech:
you cannot learn what a wording does by reading it back, only by running it and
watching what it produced.

It does not feel like code, because it has three properties ordinary code lacks. It
is **sampled, not determined**: the same prompt over the same input can come out
differently twice. It is **path-dependent**: everything the agent already holds when
it reaches your words weighs as much as the words, so the same prompt is a different
program against a different context. Its **vocabulary was found, not designed**: the
near-synonyms you would swear are equal are, to the interpreter, different programs,
so the safe refactor of real code — swap an expression for an equal one — carries no
guarantee here. "Be concise" and "say it in the fewest words that carry the point"
are two different programs.

So you do not change agent-facing prose the way you edit writing, keeping the version
that reads best. A wording is measured by what it makes the agent do, not by whether
it reads as true; a correct-but-inert line has not done its job. You run it, judge
what it produced, and guard the result against regression. The wording you are surest
of is not reliably the one that works; almost any change that reads as an improvement
can regenerate worse, and the author is the last to see it. Only the output tells you.

This is the first principle under every discipline for composing or editing
agent-facing prose. The worked technique — how to run a wording, judge its output, and
pin the result against a later edit quietly undoing it — is [tuning a
prompt](../recipes/tuning-a-prompt.md); why a flaw in such prose compounds across every
downstream read is [signal-side leverage](./signal-side-leverage.md).
