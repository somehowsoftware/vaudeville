# vaudeville-ringmaster

The assembly layer that produces and deploys the integrated Vaudeville installation on a host.

Operator lifecycle: every deploy is a Session bracketed by `ringmaster clone` (fresh-clones each Contributor Repo's `origin/main` into `~/.vaudeville/session-clones/<name>/`) and `ringmaster discard` (tears the Session down). Between them: `ringmaster stage <worktree>` materializes a Rehearsal Set as a Rehearsal Installation the operator audits and smoke-tests.

The Session forks on the smoke result:

- **Zero Rehearsal Fixes:** `ringmaster apply` builds the Artifact and hands it to the installer carried inside it, which places the Host Installation across `~/.claude/`, `~/.vaudeville/`, and `~/.local/bin/` and primes the Contributor Foundations so `vv spawn`/`vv fork` resolve without a manual re-prime: the same self-install path a tenant runs.
- **Any Rehearsal Fix at all** (even one character in one file): Deploy is blocked. Every Rehearsal Fix is productionized as a PR, reviewed and merged by the operator into the relevant Contributor's `main`, and re-pulled into a fresh Session Clone by another `ringmaster clone` before `ringmaster apply` runs. The Host Installation only ever reflects reviewed, merged code; the agent does not self-authorize an exception.

The [`/rehearse` skill](.claude/skills/rehearse/SKILL.md), invoked from a Claude Code session started in this repo, cycles Rehearsal Fixes against the Rehearsal Installation until it produces a Rehearsal Set the operator can authorize for deploy. Deploy itself is the operator's call; `/rehearse` ends at a report. The architecture and ubiquitous language live in [`docs/spec/architecture.md`](docs/spec/architecture.md) and [`docs/spec/ul.md`](docs/spec/ul.md).

## Bootstrap

Build is proprietary and runs from this source checkout; the Artifact it produces is self-installing, so the deploy runs from the repo:

```
uv run ringmaster clone      # open a Session: fresh-clone each Contributor's origin/main
uv run ringmaster apply      # build the Artifact, then activate its carried installer
uv run ringmaster discard    # close the Session
```

`apply` builds the Artifact and activates the installer carried inside it, which places the installation, installs the `vv` Facade into `~/.local/bin`, and primes the Foundations. To hand off or inspect a durable Artifact instead, `uv run ringmaster build --out <path>`; a party holding that Artifact installs it by activating its carried installer with `uv` alone, without this integrator present.

## Publish

```
uv run ringmaster clone
uv run ringmaster publish    # build the Artifact, release it to the Published Home
```

`publish` builds the install Artifact from the Session Clones and creates a versioned Release on the Published Home (`somehowsoftware/vaudeville`) carrying it: the channel a Tenant installs a named version from, rather than building from source. Alongside it, `publish` commits a readable Exposition of the same source into the Published Home's tree (`subsystems/`, `doctrine/`, `machinery/`, plus a `provenance.toml` recording each Contributor's built-from commit), so a reader browses the whole constellation at the Release's tag without cloning each repo. Like `apply`, it enforces the Pristine guard, so a Release and its Exposition reflect only reviewed, merged code. It stamps a synthetic CalVer release tag (`vYYYY.MM.DD.N`); the operator never supplies one. A fresh Published Home must already carry a base commit for the release to tag against, and the host must be able to push to its default branch. `publish` reads the elevated, Published-Home-scoped token it pushes and releases with from `[published-home].token` in the config dir's `ringmaster-credentials.toml`, an integrator-internal file the deploy never copies into `~/.vaudeville`, so the elevated token stays off the tenant runtime side (unlike `credentials.toml`, which is deployed). It does not fall back to the broad agent PR credential, and aborts before any work if that token is unset.
