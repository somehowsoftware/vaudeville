# These goals scale with agent capability

Agent capability — code quality, memory, context window — will keep improving, and the improvements exacerbate rather than relieve the problem of control: recognized as a "safety" issue, but [more salient as one of reliability](https://knightcolumbia.org/content/ai-as-normal-technology).

Do not write artefacts that assume future agents will be less capable than the one producing them. They will not be; they may be more capable, and a new model often ships between when a doctrine is written and when it is read.

Artefacts do not explain what the next agent can figure out on its own. They communicate the slice of context the next agent lacks because it was not in the conversation that produced this work. Authoring doctrine is identifying that slice, not compensating for an imagined incompetence.
