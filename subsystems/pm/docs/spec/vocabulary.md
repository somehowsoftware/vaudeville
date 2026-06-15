*This is a UL doc — terms defined in relation to one another. For framework-level UL (Bob, Premise, Route, Bounded Context, Skill, Contributor) see `~/.vaudeville/doctrine/vocabulary.md`. The doctrine for this layering is in `~/.vaudeville/doctrine/code/intent.md`.*

# vaudeville-pm vocabulary

Terms internal to vaudeville-pm, referenced in this subrepo's code, tests, and spec.

## Authoring

The act of writing a new Premise into the project tracker. Authoring composes a Premise description in the humble-snapshot shape defined in `~/.vaudeville/doctrine/practice/premise-frame.md`, sets the Route, and optionally wires Depend edges to peer Premises. The `/file` skill accomplishes it in-thread: the current agent composes the Premise and files it directly — the deliberated posture, used when the work has been thought through and full composition is earned. An optional `--spawn` chains a Bob launch onto the filed id through the bobiverse facade. The `vv file` subcommand is the single-call primitive `/file` routes through; [Tangent](#tangent)'s deterministic-capture path reuses it for the thin-signal posture.

## Claim

The Workflow transition Submitted → Claimed, or Returned → Claimed when a previously-returned Premise is picked back up. The act by which a Bob takes responsibility for a Premise. vaudeville-pm contributes the `vv premise-claim` primitive that writes this transition; the policy decision of when to claim — read the Premise, decide whether to proceed, claim only on commitment — lives in the per-Route first-turn body that vaudeville-cue renders.

## Pickable

A Premise a Bob may claim now: its Type is Premise, its Workflow is Submitted (never yet claimed) or Returned (tried and handed back), and every Premise it depends on is resolved. Pickability is the eligibility rule the pickup pool runs on. `vv available` lists the pickable Premises in a project; `vv unblocked` reports the peers a just-resolved Premise has made pickable. The rule has one definition that both reads, so the two cannot disagree about what "ready to pick up" means.

## Resolve

The resolving Premise-state transition, in two dispositions: deliver (the deliverable shipped) and abandon (the Premise should not exist anymore). Each moves the Premise to a resolved State and records a reason comment, leaving any worktree untouched. vaudeville-pm contributes the `vv resolve <delivered|abandoned>` primitive over the shared kernel's Delivered and Abandoned profiles; which disposition, and whether to resolve at all, is the closeout skill's call. *Resolve* names the lifecycle's resolving close — the Premise reaching its resolved terminus — not a programming step.

## Return

The non-resolving Premise-state transition: a Bob attempted the Premise, stopped partway, and hands it back rather than finishing. Returning moves the Premise to State Active / Workflow Returned, records a return note, and unassigns it so the Premise re-enters the pickup pool with its partial trail visible to the next picker — without tearing down any worktree. vaudeville-pm contributes the `vv return` primitive over the kernel's Returned profile.

## Tangent

A provisional Premise filed by deterministic capture rather than by [Authoring](#authoring)'s composition. A tangent is a side-concern the operator sets aside without working it out; because there is nothing yet to author — only to capture — `vv tangent` fills a fixed set of fields (the project, a title, the operator's prompt verbatim, the possibly-relevant context, and optional Depend ids) and composes the body from them with no agent discretion. The body marks the Premise provisional and reproduces the verbatim prompt as the fixed source every other field is checked against; it has no slot for a remedy or acceptance criterion, so prescriptive content has nowhere to land. The `/tangent` skill fills the form in-thread — the thin-signal posture, the operator's classifier for "I have not worked this out, capture it provisionally" — with an optional `--spawn` that mirrors `/file`'s. `vv tangent` files through the same create-plus-depend path as `vv file`, with Route fixed to `check-in`; it differs from the composed path only in that the body is captured deterministically instead of composed with discretion.

## Unblocked

The peers a resolved Premise has freed for pickup. When a Premise resolves, the peers that Depend on it may become [Pickable](#pickable). `vv unblocked` is the pure graph query that lists them, one id per line; it refuses a Premise that is not yet resolved, since an in-flight Premise has unblocked nothing. The query only reports; a closeout skill pipes its output into a spawn to act on it.
