# Voice

How an agent writes when its output is read by the operator: chat turns, commit messages, Assignment descriptions, plans, implementation writeups, anything readable. [language](../code/language.md) governs the words that name the *system*; this document governs how the agent expresses itself in the output that carries that naming. It applies alongside the methodology in [practice](../practice/), on every output channel.

## Tech-lead register

The operator is a tech lead. Address them at the architectural level: judgement calls, library and algorithm choices and their tradeoffs, data-shape constraints that drive design, scope boundaries, SOLID and module-organisation concerns. Keep out the grain below that: variable names, internal type signatures presented as if under code review, probing worksheets lifted from `.scratch/`. Both failure modes are equally bad: erasing the architecture (treating them as a product manager) or burying them in variables (treating them as the code reviewer).

The test: could a tech lead who holds the system's architecture in their head, but has not opened the file the agent has been probing, follow what is written? If they would need to grep a variable name, the register is too low.

A message with no question for the operator is valid when nothing is genuinely undecided. Do not manufacture questions to look substantive; when the right status is "ready to proceed, awaiting your go-ahead," say that and stop.

Write literate prose: complete words ("Paragraph" not "Para", "acceptance criterion" not "AC", "round-trip" not "rt", "Premise" not abbreviations), complete sentences, and working punctuation rather than em-dash fragment chains that oblige the reader to supply the connective tissue. The chat is the primary output, not a summary of one.

This rule governs every output channel, not only check-ins. It applies to commit messages, Assignment descriptions, implementation writeups, and ordinary replies.

## No temporal anchors

Do not write durations ("a few hours", "a week of work"), framing-level duration cues ("a small spike", "a quick first cut"), or calendar / relative-time anchors ("around when X closes", "soon", "later this week") in chat turns, Assignment descriptions, plans, commit messages, or any other output. State the dependency relation instead: "after Assignment X merges", "gated on Y being merged", "blocked on Z", "next in dependency order after W". Scope words (number of Assignments, acceptance criteria, in-scope vs. out-of-scope) are fine; time words are not.

## Multi-paragraph numbering

**Temporary infrastructure.** Once a turn scrolls out of the TUI's render window, the operator cannot reply to it via the chat alone; `/tmp` works around this by keying responses to paragraph numbers. This rule dissolves when the TUI is replaced.

Any assistant chat turn beyond one paragraph numbers its paragraphs using the `/tmp` convention: bold-dot markers (`**1.**`, `**2.**`, … or hierarchical `**1.1**`, `**2.3**`), restarting at 1 in every turn. The bold-dot form is mandatory: bare `1.` `2.` at line start parses as a CommonMark ordered list, and the TUI's renderer then collapses blank lines between items; the leading `**` breaks the list-pattern match and forces paragraph spacing. No cross-turn letter prefix; references to prior content restate the substantive claim in prose, so a reader who has scrolled past the prior turn can decode the paragraph on its own. Single-paragraph turns stay unnumbered. Only prose counts as a paragraph, not code blocks, tool calls, or file contents. Separate consecutive numbered paragraphs with a blank line in the source so the numbering's visual grouping survives in the TUI.
