# Drive through; redesign before escalating

Agents work autonomously and finish what they start rather than stopping for permission. When a fix is needed mid-work to keep moving, the agent makes it and continues; the operator sees it in PR review and can push back. Escalation is reserved for genuinely irreversible decisions and calls only the operator can make.

The brake on autonomous drive is bandaid accumulation. If fixes start to look like a pile of bandaids — independently-okay patches whose collective shape is incoherent — close those PRs and design a coherent change. Bandaid accumulation is the signal to *redesign*, not to *escalate*: operator review attention is scarce, and coherent design is a better use of it than adjudicating a stack of bandaids.

Pairs with [Correctness over expedience](../code/architecture.md#correctness-over-expedience) and [Portfolio, not master design](./portfolio.md).
