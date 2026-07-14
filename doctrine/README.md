# Vaudeville — the opposite of vibe coding

There are three things you can want from agentic software development tools, and this framework provides exactly one of them.

| You want     | Which means                                                                                                                  | Where to get it        |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **Velocity** | Building what you already understand, fast                                                                                   | Mainstream agent tools |
| **Reach**    | Building what you don't know how to build, but the model does                                                                | Ditto                  |
| **Depth**    | Building systems whose parts are individually intelligible but whose whole exceeds what one mind can hold in stable relation | This. Here.            |

Depth is what coding agents are supposed to be bad at: they miss the forest for the trees, they lose the thread, they develop tunnel vision, their memory is lossy. These are all true, but they are measured against the human way of building software. Agents are something else.
## Vaudeville is difficult and that is the point
Vaudeville is an implementation of a paradigm:
- Make it structurally difficult to pattern-match the agent as something it isn't.
- Treat the context window as a control surface, not as a working memory.
- Treat friction as a costly resource to be allocated.

It borrows extensively from Extreme Programming and Domain Driven Design, but it is not either of those things. In particular, it is not pair programming. 

In fact, Vaudeville is not about "programming" at all. Code quality matters in Vaudeville the way butter quality matters in baking: the good one is necessary, but neither sufficient nor worthy of long attention.  Rather, Vaudeville has more in common with a form of collaborative truth-seeking called dialectic. 

This stuffy term deserves exactly the miserable baggage it carries. Dialectic is exhausting. It requires you to be wrong and confused, a lot. It always takes longer than you expect. The fatigue and the irritation and the desire for an easy win makes it easy to fall into dialectical cosplay.
## The frontier of difficult software is vast and interesting
Most teams at most companies are building an instantiation of some familiar class of software. The best practices for these classes are well-known, and off-the-shelf agents are familiar with them. If you are building this kind of thing, Vaudeville is going to waste your time.

There also exists a category of software that rarely gets built, because it is too specialized to justify. The paradigmatic example is TeX: staggeringly useful to a small group of people, built at an outrageous cost. 

Vaudeville aims to make that kind of thing more tractable. Not easy, not fast; just tractable. The economics then become interesting. Suppose you could build a niche program that 5,000 people would really love to have. You ask for $5/mo. That's $300,000/yr, enough to more than support a solo developer. 

The set of all such niche programs is probably much larger than all existing paid software combined.
## Getting started
The components are unapologetically low-rent: it is tightly coupled to Claude Code, YouTrack, and Workmux. That's because they work, and I only wanted to build the part that I couldn't get somewhere else.

The best way to orient yourself is just to install it and try to use it for something. For that, I point you to the [Quick-Start Guide](./doctrine/quick-start.md). Once you've had a taste, check out the [concept map](./map.md) so you can get your bearings.
## Reference materials

**[The vocabulary](./doctrine/vocabulary.md)**
Vaudeville coins many terms, including some that appear at face value to be renames of more familiar concepts. These names are chosen specifically to prevent the agent from pattern-matching to inapplicable practices from human-only software development. Your agents (called "[Bobs](./doctrine/vocabulary.md#bob)") assume that you know these terms.

**[The paradigm (formerly "doctrine")](./doctrine/README.md)**
The rules by which your agents play are encoded in a paradigm to which they are oriented before every conversation. This same prose is useful reference material for the operator. 

**The Vaudeville self-tenant**
(To be reorganized). Vaudeville is self-hosted: the previous published build is used to develop the next one. The underlying source code for each release is made available in the public repository. It is a paradigmatic example of the decomposition on which Vaudeville depends.

**`vv` technical reference**
(To be authored in DOC-73.) Bobs depend on an external binary called `vv`; operators use a simpler surface called `vaudeville`. This technical reference explains how each entry point works, and how they interact.
## The theoretical framework
**You do not need to understand Vaudeville's theoretical underpinnings to use it.** They are fully encoded and encapsulated. Nevertheless, you maybe interested; Vaudeville is based on a number of things that you don't associate with engineering.

- **Philosophy.** The mode of engagement with the agent is modeled on Hegelian dialectic; the structure and language of Vaudeville is modeled as Kuhnian paradigm.
- **Human-factors engineering.** Agents are useful because they can exercise judgment. *Organizational psychology* is the study of judgment's emergent properties; the practice of directing it is called human-factors engineering. Here the factors we are directing are *half-inhuman*, but the same methodology applies.
- **Comedy.** Yes, comedy. It is a special case of human factors. This work is exhausting and miserable. It requires you to be wrong and confused, openly and in front of a judge, again and again. If you're not laughing, you're crying.

## I want to hear from you
If you are the kind of person who is interested in this work, you're probably the kind of person I'd like to meet. Please feel free to email me (`vaudeville at somehowsoftware dot com`) or [connect with me on LinkedIn](https://www.linkedin.com/in/davidborenstein/).

