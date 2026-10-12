import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "experiments.jsonl"
REPORT_FILE = ROOT / "research" / "report.md"


def display(value):
    if value is None:
        return "Not recorded"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    return str(value).replace("\n", " ").replace("|", "\\|")


def format_seconds(milliseconds):
    if not isinstance(milliseconds, (int, float)):
        return "N/A"
    return f"{milliseconds / 1000:.2f}s"


def accuracy(values):
    scored = [value for value in values if isinstance(value, bool)]
    if not scored:
        return "N/A (no scored answers)"
    correct = sum(scored)
    return f"{correct / len(scored) * 100:.2f}% ({correct}/{len(scored)})"


def mean_seconds(values):
    return format_seconds(mean(values)) if values else "N/A"


def main():
    if not DATA_FILE.exists():
        raise SystemExit(f"Experiment file not found: {DATA_FILE}")

    records = []
    malformed = 0

    # Read-only: never rewrite the experiment log.
    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if isinstance(record, dict):
                    records.append(record)
                else:
                    malformed += 1
            except json.JSONDecodeError:
                malformed += 1

    if not records:
        raise SystemExit("No valid experiment records were found.")

    # Separate the flat smoke-test schema from benchmark records.
    smoke_tests = []
    benchmarks = []
    other_records = []

    for record in records:
        if record.get("is_test") is True:
            smoke_tests.append(record)
        elif record.get("experiment_type") == "multiple_choice_benchmark":
            benchmarks.append(record)
        else:
            other_records.append(record)

    lines = [
        "# Deliberate — Experiment Report",
        "",
        f"- Total valid records: {len(records)}",
        f"- Benchmark records: {len(benchmarks)}",
        f"- Smoke-test records: {len(smoke_tests)}",
        f"- Other/legacy records: {len(other_records)}",
        f"- Malformed lines: {malformed}",
        "",
        "> Generated from saved JSONL records. The source log is not modified.",
        "",
        "## Benchmark results",
        "",
    ]

    baseline_scores = []
    debate_scores = []
    baseline_times = []
    debate_times = []
    total_costs = []
    total_tokens = []
    judge_errors = 0
    judge_error_records = 0
    unscored_baselines = 0
    unscored_debates = 0

    if not benchmarks:
        lines.extend(["No benchmark records were found.", ""])
    else:
        lines.extend([
            "| Question | Category | Expected | Baseline | Baseline correct | "
            "Baseline time | Debate | Debate correct | Debate time |",
            "|---|---|---|---|---|---:|---|---|---:|",
        ])

        for record in benchmarks:
            baseline = record.get("baseline") or {}
            debate = record.get("debate") or {}
            judge = debate.get("judge") or {}

            base_answer = baseline.get("predicted_answer")
            debate_answer = debate.get("predicted_answer")
            base_correct = baseline.get("is_correct")
            debate_correct = debate.get("is_correct")

            base_ms = baseline.get("elapsed_ms")
            debate_ms = debate.get("elapsed_ms")

            # Count only explicitly recorded boolean results.
            if isinstance(base_correct, bool):
                baseline_scores.append(base_correct)
            else:
                unscored_baselines += 1

            if isinstance(debate_correct, bool):
                debate_scores.append(debate_correct)
            else:
                unscored_debates += 1

            if isinstance(base_ms, (int, float)):
                baseline_times.append(base_ms)
            if isinstance(debate_ms, (int, float)):
                debate_times.append(debate_ms)

            # These values may be absent in older benchmark records.
            cost = record.get("cost_usd")
            tokens = record.get("total_tokens")
            if isinstance(cost, (int, float)):
                total_costs.append(cost)
            if isinstance(tokens, (int, float)):
                total_tokens.append(tokens)

            judge_error = judge.get("error")
            if not judge_error:
                judge_error = debate.get("judge_error")
            if judge_error:
                judge_errors += 1

            judge_answer = judge.get("answer")
            if judge_answer is None:
                judge_answer = judge.get("final_answer")
            if judge_answer is None:
                judge_answer = judge.get("predicted_answer")
            if judge_answer is None:
                judge_answer = debate.get("judge_answer")

            if judge_error or judge_answer is not None:
                judge_error_records += int(bool(judge_error))

            question_id = record.get("question_id", "Unknown ID")
            category = record.get("category")
            expected = record.get("correct_answer")

            lines.append(
                f"| {display(question_id)} "
                f"| {display(category)} "
                f"| {display(expected)} "
                f"| {display(base_answer)} "
                f"| {display(base_correct)} "
                f"| {format_seconds(base_ms)} "
                f"| {display(debate_answer)} "
                f"| {display(debate_correct)} "
                f"| {format_seconds(debate_ms)} |"
            )

        lines.extend([
            "",
            "## Benchmark summary",
            "",
            "| Metric | Result |",
            "|---|---:|",
            f"| Baseline accuracy | {accuracy(baseline_scores)} |",
            f"| Debate accuracy | {accuracy(debate_scores)} |",
            f"| Unscored baseline records | {unscored_baselines} |",
            f"| Unscored debate records | {unscored_debates} |",
            f"| Mean baseline latency | {mean_seconds(baseline_times)} |",
            f"| Mean debate latency | {mean_seconds(debate_times)} |",
            f"| Recorded total cost | "
            f"${sum(total_costs):.6f} ({len(total_costs)} records) |",
            f"| Recorded total tokens | "
            f"{sum(total_tokens):,} ({len(total_tokens)} records) |",
            f"| Records with a recorded judge error | {judge_errors} |",
            "",
            "> Cost and token totals include only records with those fields. "
            "Missing values are not treated as zero.",
            "",
        ])

    lines.extend([
        "## Smoke tests",
        "",
        f"- Smoke-test records: {len(smoke_tests)}",
        "- Smoke tests are excluded from benchmark accuracy.",
        "",
    ])

    for index, record in enumerate(smoke_tests, start=1):
        initial = record.get("initial_answers") or {}
        lines.extend([
            f"### Smoke test {index}: {display(record.get('question_id'))}",
            "",
            f"- Final answer: {display(record.get('final_answer'))}",
            f"- Expected answer: {display(record.get('correct_answer'))}",
            f"- Correct: {display(record.get('is_correct'))}",
            f"- Initial agent answers: {display(initial)}",
            f"- Latency: {format_seconds(record.get('latency_ms'))}",
            f"- Tokens: {display(record.get('total_tokens'))}",
            f"- Cost: {display(record.get('cost_usd'))}",
            f"- Failure tags: {display(record.get('failure_tags'))}",
            "",
        ])

    lines.extend([
        "## Interpretation notes",
        "",
        "- Benchmark baseline and debate results come from their respective "
        "nested sections.",
        "- Only explicit boolean correctness values count toward accuracy.",
        "- Missing correctness values are unscored, not incorrect.",
        "- Smoke tests and benchmark records are reported separately.",
        "- Legacy records are not silently classified as baseline or debate.",
        "- Judge errors can only be reported when the error is actually logged.",
        "- Cost and token metrics may be unavailable for older records.",
        "",
    ])

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Read {len(records)} valid records.")
    print(f"Benchmark records: {len(benchmarks)}")
    print(f"Smoke-test records: {len(smoke_tests)}")
    print(f"Other/legacy records: {len(other_records)}")
    print(f"Malformed lines: {malformed}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()