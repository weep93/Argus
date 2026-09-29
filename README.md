# Deliberate

A multi-agent AI research project exploring whether structured debate and independent reasoning can improve the quality of AI-generated conclusions.

## Research Question

> Does having multiple AI agents independently analyze and debate a question produce more reliable reasoning than asking a single AI to answer it?

## Current Architecture

```text
                    QUESTION
                       |
          +------------+------------+
          |            |            |
       Optimist     Pessimist    Logician
          |            |            |
          +------------+------------+
                       |
                Independent Analysis
                       |
                       v
                  Debate Round
                       |
                       v
                     Judge
                       |
                       v
                 Final Analysis
```

## Current Agents

### Optimist

Looks for realistic opportunities, benefits, favorable evidence, and conditions under which an outcome could succeed.

### Pessimist

Looks for failure modes, unintended consequences, risks, hidden assumptions, and reasons an outcome could fail.

### Logician

Focuses on logical consistency, evidence quality, assumptions, causal reasoning, contradictions, and uncertainty.

The personalities are intentionally different, but each agent is instructed to remain intellectually honest and update its position when presented with stronger reasoning.

## Current Experiment

The system currently tests questions with meaningful tradeoffs rather than questions with obvious answers.

Example:

> Will widespread AI automation create more economic opportunity than it destroys?

Agents first answer independently.

They then receive the other agents' arguments and participate in a second debate round. Agents are asked to identify the strongest opposing argument and report whether it changed their confidence.

A separate judge evaluates the resulting arguments.

## Research Data

Future experiments will record structured information such as:

* Initial position
* Initial confidence
* Arguments presented
* Position changes
* Confidence changes
* Strongest arguments
* Weakest arguments
* Unresolved disagreements
* Unsupported claims
* Remaining uncertainties
* Evidence that could change an agent's position

This will allow comparisons between different agent counts, models, debate structures, and judging methods.

## Current Status

**Experimental / Early Development**

The current goal is to validate the basic deliberation pipeline before expanding the system.

Planned experiments include:

* 3 → 5 → 10+ agents
* Different model families
* Multiple judges
* Multiple debate rounds
* Controlled model comparisons
* Automated question datasets
* Position and confidence tracking
* Evaluation of whether debate actually improves reasoning quality

## Tech Stack

* Python
* OpenAI-compatible API
* OpenRouter
* Concurrent agent execution
* Structured JSON evaluation *(in development)*

## Disclaimer

This project is an experiment in AI reasoning and multi-agent deliberation. Its outputs are research data and should not automatically be treated as factual or authoritative conclusions.
