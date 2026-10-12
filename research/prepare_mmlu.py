# Prepares a random sample of MMLU questions for evaluation. The sample is saved to a JSON file for use in the benchmark runner.
import json
import random
from pathlib import Path

import pyarrow.parquet as pq

SOURCE = Path("data/mmlu/test.parquet")
OUTPUT = Path("research/mmlu_sample.json")
SAMPLE_SIZE = 10
SEED = 42

table = pq.read_table(SOURCE)
rows = table.to_pylist()

random.seed(SEED)
sample = random.sample(rows, min(SAMPLE_SIZE, len(rows)))

questions = []

for index, row in enumerate(sample, start=1):
    choices = row["choices"]

    # MMLU files commonly store choices as a list of strings.
    if isinstance(choices, dict):
        choices = choices.get("text", choices)

    questions.append({
        "question_id": f"mmlu_{index:03}",
        "question": row["question"],
        "choices": {
            chr(65 + i): choice
            for i, choice in enumerate(choices)
        },
        "correct_answer": chr(65 + int(row["answer"])),
        "category": row.get("subject", "mmlu"),
    })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    json.dumps(questions, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print(f"Loaded {len(rows)} questions.")
print(f"Saved {len(questions)} questions to {OUTPUT}.")
print("First question:")
print(json.dumps(questions[0], indent=2, ensure_ascii=False))