# Installing Vaudeville

Download one self-contained release artifact, point it at a config you write, and let it install and prime itself. Nothing to clone.

> **Do this first:** install the prerequisites and fill in `credentials.toml` **before** you run the installer — it checks both and aborts if either is missing.

## Prerequisites
For the timebeing, Vaudeville depends on [workmux](https://github.com/raine/workmux) and [YouTrack](https://www.jetbrains.com/youtrack/). They are both imperfect fits and will be replaced with custom-made parts in due time. For now, you're stuck with them.

- **`uv`** on PATH — the installer runs through `uvx`. ([install](https://docs.astral.sh/uv/))
- **`workmux`** on PATH — `vv spawn`/`vv fork` use it to cut each Bob's worktree and window. ([install](https://github.com/raine/workmux))
- **A reachable YouTrack instance** — its API base URL (`https://your-instance.youtrack.cloud/api`) and a permanent token (`perm-...`).
- **`gh` or `curl`, plus `tar`** — to fetch and unpack the release.

## 1. Get the release

```sh
gh release download --repo somehowsoftware/vaudeville --pattern '*.tar.gz'
tar xzf vaudeville-v*.tar.gz
cd vaudeville-v*/
```

No `gh`? Grab the `.tar.gz` from the [latest release](https://github.com/somehowsoftware/vaudeville/releases/latest) and `tar xzf` it.

The unpacked directory is the **artifact root** (`cli/`, `data/`, `doc-trees/`, `hooks/`, `skills/`). Run the installer from inside it.

## 2. Author your config

Copy the [config template](https://github.com/somehowsoftware/vaudeville-config-template) to `~/vaudeville-config`. It holds three things:

| Path | Required | What it is |
|------|----------|------------|
| `vaudeville.toml` | yes | Project register — one repository per `[projects.<PREFIX>]` table. |
| `credentials.toml` | yes | YouTrack `api_base` + `api_key`. Gitignored; copy from `credentials-example.toml`. |
| `project-docs/` | no | Your cross-cutting docs, read by agents during priming. |

**`vaudeville.toml`** — one table per repository, keyed by its tracker prefix (`WEB-42` → `WEB`):

```toml
[projects.WEB]
repo_path   = "~/src/webshop"                        # required — clone path on this host (~ expands)
yt_id       = "0-5"                                  # required — tracker's internal project id
description = "The customer-facing storefront."      # required — Vaudeville routes work to a repo by this
remote      = "git@github.com:acme/webshop.git"      # optional — git URL; lets Vaudeville clone fresh at the current tip

[spawn.downstream]
command = ["vv", "premise-context"]                  # leave as-is
```

**`credentials.toml`** — fill in before installing:

```toml
[youtrack]
api_base = "https://your-instance.youtrack.cloud/api"
api_key  = "perm-..."
```

(`YOUTRACK_API_BASE` / `YOUTRACK_API_KEY` override these if set.)

## 3. Install

From the artifact root:

```sh
uvx --from cli/vaudeville_install-*.whl vaudeville-install \
  --artifact . \
  --destination host \
  --config-dir ~/vaudeville-config
```

`--config-dir` defaults to `~/vaudeville-config`; omit it if you used that path.

That one command:

1. **Places the scaffold** under `~/.claude/`, `~/.vaudeville/`, `~/.local/bin/`, and copies your config into `~/.vaudeville` (it reads from there, never from your config directory).
2. **Verifies the `vv` command surface.**
3. **Verifies host wiring** — YouTrack reachable, `workmux` runnable. **Aborts here if either fails.**
4. **Primes the Foundations** (`vv prime`) — one per project — and confirms them.

Priming is built in. You don't run it yourself.

## After installing

- `vv` lives in `~/.local/bin`. Add that to your PATH if it isn't already.
- Changed your config or doctrine? Re-prime with `vv prime`.
- The unpacked artifact is safe to delete — everything now lives under `~/.claude`, `~/.vaudeville`, and `~/.local/bin`.
