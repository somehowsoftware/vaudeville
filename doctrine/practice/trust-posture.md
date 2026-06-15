# Trust posture

Agents in Vaudeville are not adversarial. Drift, hallucination, and misunderstanding are real failure modes; malice is not. The market incentives of frontier labs make adversarial behavior costly to ship and short-lived to survive. The modal agent failure is a confident wrong answer, not defection.

A successful prompt-injection attack can turn the conversation malicious in real terms: a compromised model executes the attacker's instructions in the moment, and the conversation's outputs can corrupt subsequent agents whose work inherits them. The model itself, however, remains the same model — shaped by the same profit motive that disfavored shipping adversarial behavior in the first place. There is no straightforward mechanism for an attacker to turn it into a strategic adversary, and no economic incentive for anyone to find one.

The threat model: attackers seek exfiltration or ransom; the mitigation is treating the environment as pre-compromised and locating the trust boundary outside the conversation. Claude Code's auto mode — a secondary review loop in which an off-machine agent screens the local conversation's tool calls and cannot be co-opted by anything inside the conversation — is the defense-in-depth layer for prompt injection; the framework's deployed configuration enables it.

Operational consequences: agents work inside an isolated environment — a host treated as pre-compromised, with broad authority inside the isolation. Human oversight lands at the outcome layer rather than the action layer, on the premise that decision-fatigued micro-permissioning produces worse outcomes than attentive perimeter review.
