import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# // config

JUDGE_MODEL = "openrouter/free" # temporary they removed my beautiful deekseek from me :(

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def final_answer(user_prompt, initial_results, debate_results):
    """Judge the independent arguments and the subsequent debate."""

    initial_good = [
        r for r in initial_results
        if r["answer"] and not r["error"]
    ]

    debate_good = [
        r for r in debate_results
        if r["answer"] and not r["error"]
    ]

    if not initial_good:
        return {
            "answer": "Every initial agent failed.",
            "by": None,
        }

    # Build Round 1 transcript
    initial_blocks = []

    for r in initial_good:
        initial_blocks.append(
            "--- " + r["agent"] + " INITIAL POSITION ---\n"
            + r["answer"]
        )

    initial_transcript = "\n\n".join(initial_blocks)

    # Build Round 2 transcript
    debate_blocks = []

    for r in debate_good:
        debate_blocks.append(
            "--- " + r["agent"] + " DEBATE RESPONSE ---\n"
            + r["answer"]
        )

    debate_transcript = "\n\n".join(debate_blocks)

    ask = f"""
You are an independent debate judge.

Your job is NOT to choose the most popular argument.

Evaluate the reasoning objectively.

ORIGINAL QUESTION:

{user_prompt}


================ ROUND 1: INITIAL POSITIONS ================

{initial_transcript}


================ ROUND 2: DEBATE ================

{debate_transcript}


Evaluate the arguments using:

- logical consistency
- evidence
- assumptions
- counterarguments
- uncertainty
- unsupported claims
- internal contradictions
- whether conclusions actually follow from the evidence

Identify:

1. strongest arguments
2. weakest arguments
3. unresolved disagreements
4. arguments that changed during the debate
5. areas where participants incorrectly assumed consensus
6. important uncertainties
7. claims that would require additional evidence

Do NOT decide based on:
- popularity
- how confidently an agent writes
- which agent spoke last
- majority opinion
- personality

If an argument is strong even though only one agent made it, recognize that.

If all agents share the same unsupported assumption, explicitly identify it.

If the debate did not resolve an issue, say that it remains unresolved.

Return ONLY valid JSON using this exact structure:

{{
    "strongest_arguments": [],
    "weakest_arguments": [],
    "unresolved_disagreements": [],
    "position_changes": [],
    "false_consensus": [],
    "uncertainties": [],
    "claims_needing_evidence": [],
    "final_synthesis": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": ask,
                }
            ],
        )

        raw = response.choices[0].message.content

        # Validate that the judge actually returned JSON
        try:
            judged = json.loads(raw)

            return {
                "answer": json.dumps(
                    judged,
                    indent=2,
                ),
                "by": "judge",
            }

        except json.JSONDecodeError:
            # Judge answered but ignored the JSON requirement
            return {
                "answer": raw,
                "by": "judge",
            }

    except Exception as e:
        # Judge failed: preserve the debate instead of losing everything
        return {
            "answer": (
                "Judge failed (" + str(e) + ").\n\n"
                "ROUND 1:\n\n"
                + initial_transcript
                + "\n\nROUND 2:\n\n"
                + debate_transcript
            ),
            "by": "judge-error",
        }