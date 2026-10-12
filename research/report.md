# Deliberate — Experiment Report

- Total valid records: 15
- Benchmark records: 13
- Smoke-test records: 2
- Other/legacy records: 0
- Malformed lines: 0

> Generated from saved JSONL records. The source log is not modified.

## Benchmark results

| Question | Category | Expected | Baseline | Baseline correct | Baseline time | Debate | Debate correct | Debate time |
|---|---|---|---|---|---:|---|---|---:|
| math_001 | math | B | Not recorded | Not recorded | 4.73s | B | Yes | 33.07s |
| science_001 | science | C | C | Yes | 1.95s | C | Yes | 131.00s |
| computing_001 | computing | B | B | Yes | 4.59s | B | Yes | 80.54s |
| mmlu_001 | miscellaneous | B | B | Yes | 22.38s | B | Yes | 98.41s |
| mmlu_002 | electrical_engineering | C | Not recorded | Not recorded | 1.01s | C | Yes | 90.46s |
| mmlu_003 | security_studies | B | B | Yes | 12.26s | B | Yes | 86.63s |
| mmlu_004 | elementary_mathematics | A | Not recorded | Not recorded | 3.05s | A | Yes | 42.44s |
| mmlu_005 | high_school_mathematics | C | C | Yes | 105.69s | C | Yes | 108.22s |
| mmlu_006 | professional_psychology | C | C | Yes | 4.57s | D | No | 255.32s |
| mmlu_007 | professional_psychology | A | A | Yes | 7.62s | A | Yes | 101.50s |
| mmlu_008 | nutrition | A | A | Yes | 33.89s | C | No | 121.96s |
| mmlu_009 | elementary_mathematics | B | C | No | 124.76s | B | Yes | 111.10s |
| mmlu_010 | astronomy | C | C | Yes | 0.91s | C | Yes | 58.17s |

## Benchmark summary

| Metric | Result |
|---|---:|
| Baseline accuracy | 90.00% (9/10) |
| Debate accuracy | 84.62% (11/13) |
| Unscored baseline records | 3 |
| Unscored debate records | 0 |
| Mean baseline latency | 25.19s |
| Mean debate latency | 101.45s |
| Recorded total cost | $0.000000 (0 records) |
| Recorded total tokens | 0 (0 records) |
| Records with a recorded judge error | 0 |

> Cost and token totals include only records with those fields. Missing values are not treated as zero.

## Smoke tests

- Smoke-test records: 2
- Smoke tests are excluded from benchmark accuracy.

### Smoke test 1: fake_question_001

- Final answer: B
- Expected answer: B
- Correct: Yes
- Initial agent answers: {"optimist": "A", "logician": "B", "pessimist": "C"}
- Latency: 3.50s
- Tokens: 1200
- Cost: 0.002
- Failure tags: []

### Smoke test 2: fake_question_001

- Final answer: B
- Expected answer: B
- Correct: Yes
- Initial agent answers: {"optimist": "A", "logician": "B", "pessimist": "C"}
- Latency: 3.50s
- Tokens: 1200
- Cost: 0.002
- Failure tags: []

## Interpretation notes

- Benchmark baseline and debate results come from their respective nested sections.
- Only explicit boolean correctness values count toward accuracy.
- Missing correctness values are unscored, not incorrect.
- Smoke tests and benchmark records are reported separately.
- Legacy records are not silently classified as baseline or debate.
- Judge errors can only be reported when the error is actually logged.
- Cost and token metrics may be unavailable for older records.

