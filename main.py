# main.py : router -> agents -> judge | get_logs tool wired in | rewritten 2026-09-11
import json
import os
import time
import uuid
from research.logger import log_experiment 



from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv

from openai import OpenAI

from tools.get_logs import get_logs

from judge import final_answer

from router import pick_agents


from pathlib import Path

load_dotenv()


# // config

MAX_TOOL_ROUNDS = 4 # how many times an agent can call tools before we stop it

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


# defining the tools the agents are allowed to call

TOOL_REGISTRY = {
    "get_logs": get_logs,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Read recent log lines for an allowed service. Use when asked what a service is doing, why it failed, or for recent activity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unit": {
                        "type": "string",
                        "enum": ["weep-manager", "weep-site", "nginx", "fail2ban", "ssh", "kage-web"],
                        "description": "which service to read logs for",
                    },
                    "lines": {
                        "type": "integer",
                        "description": "lines to return, 1-200 (default 50)",
                    },
                },
                "required": ["unit"],
            },
        },
    },
]


# defining the agents, used AI to summarize a computer optimized personality

AGENTS_DIR = Path(__file__).resolve().parent / "agents"

AGENTS = {
    "optimist": {
        "model": "openrouter/free",
        "tools": [],
    },
    "pessimist": {
        "model": "openrouter/free",
        "tools": [],
    },
    "logician": {
        "model": "openrouter/free",
        "tools": [],
    },
}

for name, config in AGENTS.items():
    prompt_path = AGENTS_DIR / f"{name}.md"
    config["system"] = prompt_path.read_text(encoding="utf-8")




def build_debate_prompt(user_prompt, results):
    transcript = "\n\n".join(
        f"==== {r['agent'].upper()} ====\n{r['answer']}"
        for r in results
        if not r["error"]
    )

    return f"""
You are participating in a structured debate.

ORIGINAL QUESTION:
{user_prompt}

OTHER PARTICIPANTS' INITIAL ARGUMENTS:

{transcript}

Respond to the other participants.

You MUST:

1. Identify the strongest argument against your position.
2. Explain whether you agree or disagree with it.
3. Identify a weakness in at least one opposing argument.
4. Address any unsupported assumptions.
5. State whether the opposing arguments changed your confidence.
6. Do not agree merely because another agent sounds convincing.

Attack arguments, not participants.

Your response should focus on reasoning rather than repeating your
original answer.
"""

# defining the worker structure

def run_agent(name, cfg, user_prompt):
    messages = [
        {"role": "system", "content": cfg["system"]},
        {"role": "user", "content": user_prompt},
    ]

    attempts = 0

    # only hand over the tools this agent is allowed to use
    schema = [t for t in TOOL_SCHEMAS if t["function"]["name"] in cfg["tools"]]

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            kwargs = {"model": cfg["model"], "messages": messages}
            if schema:
                kwargs["tools"] = schema

            response = client.chat.completions.create(**kwargs)
            msg = response.choices[0].message

            # no tool call : normal answer, we are done
            if not msg.tool_calls:
                return {
                    "agent": name,
                    "answer": msg.content,
                    "error": None
                }

            # the model asked for tools : run them and feed the results back
            messages.append(msg)

            for call in msg.tool_calls:
                tool = TOOL_REGISTRY.get(call.function.name)

                if tool is None:
                    result = {"ok": False, "error": "unknown tool " + call.function.name}

                else:
                    try:
                        args = json.loads(call.function.arguments or "{}")
                        result = tool(**args)

                    except Exception as e:
                        result = {"ok": False, "error": str(e)}

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)[:4000] # keep big logs out of context
                })

        except Exception as e:

            # api hiccup or rate limit : wait a moment and try the whole round again
            if attempts < 1:
                attempts += 1
                time.sleep(3)
                continue

            return {
                "agent": name,
                "answer": None,
                "error": str(e)
            }

    return {
        "agent": name,
        "answer": "(stopped : too many tool rounds)",
        "error": None
    }


# running the agents

def run_agents(user_prompt, names=None):
    results = []

    todo = [n for n in (names or AGENTS.keys()) if n in AGENTS]

    with ThreadPoolExecutor(max_workers=len(todo)) as executor:

        futures = [
            executor.submit(
                run_agent,
                name,
                AGENTS[name],
                user_prompt,
            )
            for name in todo
        ]

        for future in as_completed(futures):
            results.append(future.result())

    return results


def run_debate_round(user_prompt, results):
    debate_prompt = build_debate_prompt(user_prompt, results)

    debate_results = []

    with ThreadPoolExecutor(max_workers=len(AGENTS)) as executor:
        futures = [
            executor.submit(
                run_agent,
                name,
                AGENTS[name],
                debate_prompt,
            )
            for name in AGENTS
        ]

        for future in as_completed(futures):
            debate_results.append(future.result())

    return debate_results


# main

def main():

    print(r"""
  .-')                _  .-')  _  .-')                 (`\ .-') /` 
 ( OO ).             ( \( -O )( \( -O )                 `.( OO ),' 
(_)---\_) .-'),-----. ,------. ,------.  .-'),-----. ,--./  .--.   
/    _ | ( OO'  .-.  '|   /`. '|   /`. '( OO'  .-.  '|      |  |   
\  :` `. /   |  | |  ||  /  | ||  /  | |/   |  | |  ||  |   |  |,  
 '..`''.)\_) |  |\|  ||  |_.' ||  |_.' |\_) |  |\|  ||  |.'.|  |_) 
.-._)   \  \ |  | |  ||  .  '.'|  .  '.'  \ |  | |  ||         |   
\       /   `'  '-'  '|  |\  \ |  |\  \    `'  '-'  '|   ,'.   |   
 `-----'      `-----' `--' '--'`--' '--'     `-----' '--'   '--'   
    """)


    print("Multi Agent Starting...")

    user_input = input("\ncupid: ")


    # initalizing ID/STARTED
    experiment_id = str(uuid.uuid4())
    experiment_started = time.perf_counter()

    print("\n=== ROUND 1: INDEPENDENT ANALYSIS ===")

    results = run_agents(user_input)

    for result in results:
        print(f"\n==== {result['agent'].upper()} ====")

        if result["error"]:
            print("[ERROR]", result["error"])
        else:
            print(result["answer"])

        print()

    print("\n=== ROUND 2: DEBATE ===")

    debate_results = run_debate_round(user_input, results)

    for result in debate_results:
        print(f"\n==== {result['agent'].upper()} DEBATE ====")

        if result["error"]:
            print("[ERROR]", result["error"])
        else:
            print(result["answer"])

        print()

    print("\n=== JUDGE ===")

    final = final_answer(
        user_input,
        results,
        debate_results,
    )

    print("\n==== FINAL (" + str(final["by"]) + ") ====")
    print(final["answer"])

    # // DATA TO BE WRITTEN TO LOG
    elapsed_ms = round(
        time.perf_counter() - experiment_started) * 1000
    record = {
        "experiment_id": experiment_id,
        "condition": "three_agent_debate",
        "experiment_type": "interactive_unscored",
        "question_id": None,
        "question": user_input,

        "agent_models" : {
            name: config["model"] 
            for name, config in AGENTS.items()
        },

        "initial_results": results,
        "debate_results": debate_results,

        "judge": final, 
        "judge_model": "deepseek/deepseek-chat:free",

        "elapsed_ms": elapsed_ms,


        # // NO ANWSER KEY AVAILBLE IN INTERACTIVE
        "correct_answer": None,
        "is_correct": None, 
        "scoring_-status": "not_scored", 
    }


    try: 
        log_experiment(record)
        print(f"\n[Research] Experiment saved: {experiment_id}")
    except Exception as e:
        print(f"\n[Research] Logging failed: {e}")

if __name__ == "__main__":
    main()
