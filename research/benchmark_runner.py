import json
import re
import time
import uuid
from pathlib import Path

from main import AGENTS, run_agents, run_debate_round
from judge import client, JUDGE_MODEL, final_answer
from research.logger import log_experiment

import sys

BENCHMARK_PATH = Path(
    sys.argv[1] if len(sys.argv) > 1 else "research/benchmark.json"
)


BASELINE_MODEL = "openrouter/free"


def ask_baseline(question, choices):
    prompt = f"""
Answer this multiple-choice question.
Choose exactly one option: A, B, C, or D.

Question: {question}

{chr(10).join(f"{key}: {value}" for key, value in choices.items())}

Return only the letter of your answer.
"""
    response = client.chat.completions.create(
        model=BASELINE_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def extract_choice(text):
    if not text:
        return None

    # Prefer an explicit answer declaration.
    patterns = [
        r"(?i)\banswer\s*(?:is|:|=)\s*[\(\[]?([ABCD])\b",
        r"(?i)\boption\s+([ABCD])\b",
        r"(?i)^\s*[\(\[]?([ABCD])[\)\].:\s]*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text.strip())
        if match:
            return match.group(1).upper()

    # Avoid guessing if the response is ambiguous.
    return None


def make_debate_question(question, choices):
    options = "\n".join(
        f"{letter}: {value}" for letter, value in choices.items()
    )
    return f"""
Answer this multiple-choice question using the choices provided.

Question: {question}

{options}

Reason carefully. In your final answer, explicitly state:
ANSWER: <one letter A, B, C, or D>
"""


def main():
    with BENCHMARK_PATH.open(encoding="utf-8") as file:
        questions = json.load(file)

    baseline_correct = 0
    debate_correct = 0
    baseline_scored = 0
    debate_scored = 0

    for item in questions:
        question_id = item["question_id"]
        question = item["question"]
        choices = item["choices"]
        correct = item["correct_answer"].upper()

        print(f"\n{'=' * 60}")
        print(f"{question_id}: {question}")

        # Condition A: single-model baseline
        start = time.perf_counter()
        try:
            baseline_raw = ask_baseline(question, choices)
            baseline_error = None
        except Exception as exc:
            baseline_raw = ""
            baseline_error = str(exc)

        baseline_ms = round((time.perf_counter() - start) * 1000)
        baseline_choice = extract_choice(baseline_raw)
        baseline_is_correct = (
            baseline_choice == correct if baseline_choice else None
        )

        # Condition B: three-agent debate
        debate_prompt = make_debate_question(question, choices)
        start = time.perf_counter()

        initial_results = run_agents(debate_prompt)
        debate_results = run_debate_round(debate_prompt, initial_results)
        judge_result = final_answer(
            debate_prompt, initial_results, debate_results
        )

        debate_ms = round((time.perf_counter() - start) * 1000)

        judge_text = judge_result.get("answer", "")
        debate_choice = extract_choice(judge_text)
        debate_is_correct = (
            debate_choice == correct if debate_choice else None
        )

        if baseline_is_correct is not None:
            baseline_scored += 1
            baseline_correct += int(baseline_is_correct)

        if debate_is_correct is not None:
            debate_scored += 1
            debate_correct += int(debate_is_correct)

        record = {
            "experiment_id": str(uuid.uuid4()),
            "experiment_type": "multiple_choice_benchmark",
            "question_id": question_id,
            "category": item.get("category"),
            "question": question,
            "choices": choices,
            "correct_answer": correct,
            "baseline": {
                "model": BASELINE_MODEL,
                "raw_answer": baseline_raw,
                "predicted_answer": baseline_choice,
                "is_correct": baseline_is_correct,
                "elapsed_ms": baseline_ms,
                "error": baseline_error,
            },
            "debate": {
                "agent_models": {
                    name: config["model"]
                    for name, config in AGENTS.items()
                },
                "initial_results": initial_results,
                "debate_results": debate_results,
                "judge": judge_result,
                "judge_model": JUDGE_MODEL,
                "predicted_answer": debate_choice,
                "is_correct": debate_is_correct,
                "elapsed_ms": debate_ms,
            },
        }

        log_experiment(record)

        print(f"Correct answer: {correct}")
        print(f"Baseline: {baseline_choice} | correct: {baseline_is_correct}")
        print(f"Debate:   {debate_choice} | correct: {debate_is_correct}")
        print("Saved result to data/experiments.jsonl")

    print("\n===== BENCHMARK SUMMARY =====")
    print(
        f"Baseline: {baseline_correct}/{baseline_scored} scored "
        f"({baseline_correct / baseline_scored:.1%})"
        if baseline_scored else "Baseline: no answers could be scored"
    )
    print(
        f"Debate:   {debate_correct}/{debate_scored} scored "
        f"({debate_correct / debate_scored:.1%})"
        if debate_scored else "Debate: no answers could be scored"
    )
    print("Unparseable answers are left unscored, not counted as correct.")


if __name__ == "__main__":
    main()
