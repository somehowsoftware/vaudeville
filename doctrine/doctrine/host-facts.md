# Host facts

Doctrine is portable across hosts and tenants; hosts are not. Per-install facts live in `~/.vaudeville/host.md`, an optional gitignored file the operator hand-curates. Priming reads it after the framework doctrine. Plain markdown: short sections naming each fact, no template, no schema. If the file does not exist, priming picks nothing up; the framework does not require it.

AI never writes to `host.md`; the operator owns it. If an agent decides a fact belongs there, it surfaces the candidate in chat for the operator to add by hand. Agent writes to this path are denied mechanically.
