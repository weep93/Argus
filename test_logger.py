
from research.logger import log_experiment

fake_experiment = {
    "experiment_id": "test_001",
    "question_id": "fake_question_001",
    "condition": "three_agent_debate",
    "is_test": True,

    "initial_answers": {
        "optimist": "A",
        "logician": "B",
        "pessimist": "C"
    },

    "final_answer": "B",
    "correct_answer": "B",
    "is_correct": True,

    "total_tokens": 1200,
    "latency_ms": 3500,
    "cost_usd": 0.002,

    "failure_tags": []
}

log_experiment(fake_experiment)

print("Fake experiment logged successfully.")
