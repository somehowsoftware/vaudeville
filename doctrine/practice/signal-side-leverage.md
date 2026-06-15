# Signal-side leverage under noisy measurement

The rate-limiting failure mode in Vaudeville is information corruption across lossy transmissions: specs into Premises, Premises into prep, prep into a [Bob](../vocabulary.md#bob)'s work, work into code. Measurement of where corruption concentrates is itself noisy: failures are randomly distributed and discrete.

Under noisy measurement, fixes at the producer end of a chain — better specs, better Premises, less ambiguous skills — compound across every downstream read. Fixes at the consumer end — better prep, better review — help once, at the read site. Prefer signal-side fixes; they multiply.

Prefer cheap, legible producer-side fixes over expensive ones: measurement noise means a big bet on one intervention can fail to move the system measurably even when correctly aimed, while a cheap fix gives a real result and a cleaner reading of the next bottleneck.

This is orthogonal to storage medium (agent memory systems, code-review pipelines). The bottleneck is the lossiness of the chain of custody at each transmission boundary, not memory capacity or code quality.
# Place premise boundaries to maximize coherence
Every boundary loses signal, so chosen boundaries deserve deliberate placement. A Premise boundary leaks — whatever the upstream understood that does not cross the edge is gone — while it contains, sparing the downstream agent the rest. Place Premise boundaries where the dependency graph is cheap to traverse: a narrow, named contract crossing each edge, not reasoning the reader must reconstruct.
