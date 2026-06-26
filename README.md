# Vaudeville: a tool for the opposite of vibe coding

Vaudeville is a tool for developing software slowly. Its method is called *dialectical engineering*. Its doctrine cites [Hegel](https://en.wikipedia.org/wiki/Dialectic#Hegelian_dialectic), [the Talmud](https://en.wikipedia.org/wiki/Chavrusa#Practice), and [crew resource management](https://en.wikipedia.org/wiki/Crew_resource_management#Emphasis_on_non-technical_skills). Its name comes from a [dead theatrical form](https://en.wikipedia.org/wiki/Vaudeville). When you say it out loud, it sounds stupid; it reliably earns skepticism, eye-rolls, and occasionally outright pity. These are all reasonable reactions.

The point is to build software that neither a human nor an agent could build alone. Most useful software is not that. Most of the time, Vaudeville is the wrong tool for the job. It's the right tool when you want to [build a to-do app](./the-point.md#velocity-reach-depth) with the level of rigor usually reserved for spacecraft guidance systems.

Uncharitably, Vaudeville is for glorious over-engineering. [Donald Knuth spent twelve years inventing TeX](https://en.wikipedia.org/wiki/TeX#History). If you ever looked at that and thought, "I wish that were me," this could be a nice tool for you.

## The enemy

The enemy is plausible code that quietly changes what the system means. A predicate becomes a filter. A filter becomes a state transition. A user-interface metaphor becomes a domain primitive. Every diff reads as reasonable, and the system ends up wrong in a way that only surfaces when the parts have to compose.

## You probably don't need this

Most useful new software is similar to one or another class of useful existing software. That's great, because it means that agents can pick up the thread and run with it. Vaudeville is 4WD low: you'll go slower on every road but the one that would have stopped you. If you are building software that can be understood as "the same kind of thing as X, but retargeted at/optimized for/designed around Y", this is not the droid you're looking for.

Vaudeville is built for systems where:
1. each part is individually intelligible, and yet
2. the total coordination burden exceeds what one mind can hold in stable relation long enough to build them. 

If you are staring at such a problem, this framework stops being philosophy and starts being the most practical tool available.

## You probably won't like this

The framework is opinionated in directions that are largely abandoned because they are usually overkill. Two key points on this:

- **It is XP and domain-driven design taken at full strength:** tests written before the code and named as contracts, a ubiquitous language that is enforced rather than encouraged, bounded contexts with real borders, docstrings banned, comments nearly banned, acceptance criteria banned from premises.

- **It manufactures friction on purpose.** The characteristic unit of work is not a ticket, but a _premise_. The agent is under standing instruction to oppose you. If what you want is an amiable executor of instructions, this will be a miserable fit. The friction is the product: the argument is where the work gets done that neither party could have done alone.

## The code here is reorganized for reading

The tree in this repository is not the source as it is developed: it has been reorganized for legibility. This mechanism also lets me write my drafts unobserved. Keeping the [Components](./doctrine/vocabulary.md#component) private allows me to celebrate, despair, curse, kvetch, berate, and laugh at my own jokes in private. 

Dialectical engineering is [designed to surface misconceptions](./the-point.md). The process depends on you being _wrong_, _confused_, and _ignorant_. Doing that in front of an audience changes the character of that work.

## Getting started

### Key resources
- [Prerequisites](./prerequisites.md): whether you should use Vaudeville at all.
- [Concepts](./concepts.md): the vocabulary built up as exposition.
- [Walkthrough](walkthrough.md): a tour of how Vaudeville is built using Vaudeville.
- [Workflow](./workflow.md): the day-to-day process of working in Vaudeville.
- [Installation](./installation.md): the mechanics of starting your Vaudeville project.

### Additional reading
- [The point](./the-point.md): optimistically, an essay on what Vaudeville is for. Pessimistically, a screed.
- [Weaponized philosophy](./weaponized-philosophy.md): where the practices come from.
- [Glossary](doctrine/vocabulary.md): the reference version of [Concepts](./concepts.md).
