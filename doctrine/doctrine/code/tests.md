# Tests

How we verify the system: what a test is for, how it is named, what counts as testing theater.

## Tests are specifications

Tests declare what a unit promises, in the domain's own terms: test names state contracts, bodies prove them. Regression prevention is a side effect, not the purpose.

If you cannot articulate the core tests, you are not ready to write the code. Each test answers "what contract does this unit guarantee?" If no clear answer exists, the contract is undetermined, and writing the code only entrenches the ambiguity.

Tests of getters, framework internals, trivial forwarding, or whose names describe mechanics rather than promises are testing theater: they dilute the real contracts and accumulate maintenance cost without proportional value.

## Tests carry the low-level WHAT

The test suite is the executable specification of behaviour at the unit level. If a document would say what a test could pin, the test wins: the layering principle in [intent](./intent.md) applied to verification.
