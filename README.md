# Deliberate

A multi-agent AI research project exploring whether structured debate and independent reasoning can improve the quality, reliability, and correctness of AI-generated conclusions.

## Research Question

> Does having multiple AI agents independently analyze and debate a question produce more reliable reasoning than asking a single AI to answer it?

## Current Architecture

```text
                         QUESTION
                            |
             +--------------+--------------+
             |              |              |
          Optimist       Pessimist       Logician
             |              |              |
             +--------------+--------------+
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

The research pipeline also includes a single-model baseline for comparing performance against the multi-agent approach.

## Current Agents

### Optimist

Looks for realistic opportunities, benefits, favorable evidence, and conditions under which an outcome could succeed.

### Pessimist

Looks for failure modes, unintended consequences, risks, hidden assumptions, and reasons an outcome could fail.

### Logician

Focuses on logical consistency, evidence quality, assumptions, causal reasoning, contradictions, and uncertainty.

The personalities are intentionally different, but each agent is instructed to remain intellectually honest and update its position when presented with stronger reasoning.

## The Judge

The judge evaluates the agents' initial arguments and debate responses.

Its current analysis considers:

- Strongest and weakest arguments
- Unresolved disagreements
- Changes in agent positions
- Potential false consensus
- Remaining uncertainties
- Claims requiring additional evidence
- Final synthesis of the discussion

The judge is a separate evaluation component, not a guaranteed source of truth. Its conclusions can be incorrect and must be evaluated independently.

## Current Experiment

The project now has an initial multiple-choice benchmark at `research/benchmark.json`.

The benchmark runner compares two conditions:

**Single-model baseline**
- One model answers each question without multi-agent debate.

**Three-agent debate**
- Optimist, Pessimist, and Logician independently respond.
- Each agent participates in a debate round.
- The judge evaluates the resulting arguments and produces a synthesis.

The runner compares predictions against the benchmark's answer key and records experiment data in `data/experiments.jsonl`.

### Initial Pipeline Test

The first benchmark contains three basic questions covering mathematics, science, and computing.

| Condition | Scored answers | Correct | Accuracy |
|---|---:|---:|---:|
| Single-model baseline | 2 | 2 | 100% |
| Three-agent debate | 3 | 3 | 100% |

**Important limitations:**

- One baseline answer could not be parsed into a multiple-choice selection, so it was excluded from the baseline score.
- The benchmark contains only three relatively straightforward questions.
- The models use free OpenRouter routing, which may not guarantee a consistent underlying model.
- These results validate an initial pipeline run; they do not demonstrate that debate improves accuracy.

The next step is to improve answer extraction, make the scoring process reliable, and expand the benchmark before drawing conclusions.

## Research Data

Experiments are recorded as JSON Lines in `data/experiments.jsonl`.

The current records include information such as:

- Experiment and question identifiers
- Question category and prompt
- Available choices and correct answer
- Baseline model and prediction
- Initial agent responses
- Debate responses
- Judge output and model
- Correctness results
- Execution time

Future experiments will track additional measures where appropriate:

- Initial position and confidence
- Position changes after debate
- Confidence changes
- Argument quality
- Unsupported claims
- Unresolved disagreements
- Evidence that could change an agent's position

## Scoring Rubric

### 1. Correctness — Primary Metric

- **1:** Prediction matches the benchmark answer key.
- **0:** Prediction is incorrect, unanswered, or invalid.

Unparseable predictions should be recorded separately during development so that answer-formatting failures can be distinguished from reasoning failures. Final accuracy calculations should use a consistent, explicitly documented denominator.

### 2. Evidence and Reasoning Quality

- **0:** No relevant justification.
- **1:** Weak justification with major gaps.
- **2:** Sound, relevant justification supporting the answer.
- **3:** Strong, relevant justification that supports the answer with clear reasoning and appropriate evidence.

### 3. Unsupported Claims

- **0:** No material unsupported claims detected.
- **1:** One questionable claim.
- **2:** Multiple or significant unsupported claims.

These rubric dimensions are proposed evaluation criteria; they require consistent scoring procedures before they can support meaningful comparisons.

## Experimental Principles

To investigate whether debate adds value:

- Use the same questions across comparison conditions.
- Keep model choices and configurations documented.
- Compare the baseline and debate system on the same benchmark.
- Record failed, invalid, and unparseable outputs.
- Track execution time as well as answer quality.
- Expand the dataset before making broad claims.
- Avoid treating judge confidence or agent consensus as proof of correctness.

## Planned Experiments

- [ ] Fix baseline answer parsing and scoring.
- [ ] Add progress reporting and API timeouts.
- [ ] Expand the benchmark with varied difficulty levels.
- [ ] Compare baseline and debate accuracy on identical questions.
- [ ] Evaluate evidence and reasoning quality.
- [ ] Measure unsupported claims and unresolved uncertainty.
- [ ] Compare different model families.
- [ ] Test multiple judges.
- [ ] Compare different numbers of agents: 3, 5, and 10+.
- [ ] Investigate multiple debate rounds.
- [ ] Track position and confidence changes.
- [ ] Evaluate whether debate improves results enough to justify its additional latency and API usage.

## Tech Stack

- Python
- OpenAI-compatible API
- OpenRouter
- Concurrent agent execution
- JSON-based benchmark dataset
- JSON Lines experiment logging
- Structured judge evaluation

## Current Status

**Experimental / Early Development**

The basic deliberation pipeline and an initial benchmark run are working. Reliable scoring, broader evaluation, and controlled comparisons remain ongoing work.

## Disclaimer

Deliberate is an experimental research project exploring AI reasoning and multi-agent deliberation. Its outputs are research data and should not automatically be treated as factual or authoritative conclusions.