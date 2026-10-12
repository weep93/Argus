import json 
from pathlib import Path
from datetime import datetime, timezone

DATASET_PATH = Path("data/experiments.jsonl") 


def log_experiment(record : dict) -> None: 
    """Append a record to the experiments log file"""
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True) #creates missing parent directory path

    entry = {
        "schema_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }

    with DATASET_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
