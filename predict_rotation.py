"""
Narrative Rotation Forecaster
==============================
Predicts which narrative is likely to receive capital rotation next,
based on current lifecycle stages, velocity scores, and historical
rotation patterns in crypto markets.
"""

import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ROTATION_PROMPT = """You are a crypto narrative rotation analyst for the Attention Arbitrage Engine.

Your job is to analyze a set of classified narratives and predict which narrative
is most likely to receive capital rotation next.

Rotation logic:
- Capital flows FROM saturating narratives TO emerging ones
- When a dominant narrative peaks, adjacent or contrasting narratives benefit
- Infrastructure narratives often follow speculative narrative peaks
- Meme narratives often rotate into utility narratives after peak

You will receive a list of currently classified narratives with their lifecycle stages.

Respond ONLY with valid JSON:
{
  "current_leader": "narrative currently receiving most attention",
  "rotation_target": "narrative most likely to receive capital next",
  "rotation_confidence": 0.0,
  "rotation_trigger": "what event or condition would trigger this rotation",
  "estimated_rotation_days": 0,
  "reasoning": "2-3 sentence explanation",
  "watchlist": ["narrative1", "narrative2"]
}"""


def predict_rotation(classifications):
    """
    Takes classified narratives and predicts next rotation target.
    """
    narrative_summary = []
    for item in classifications:
        c = item["classification"]
        e = item["enriched"]
        narrative_summary.append({
            "name": c["narrative_name"],
            "lifecycle_stage": c["lifecycle_stage"],
            "opportunity_score": c["opportunity_score"],
            "velocity_score": e["velocity_score"],
            "relative_attention_alpha": e.get("relative_attention_alpha", 0),
            "estimated_half_life_days": c.get("estimated_half_life_days", 30),
            "historical_analog": c.get("historical_analog", {}).get("match", "Unknown"),
        })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ROTATION_PROMPT},
            {"role": "user", "content": json.dumps(narrative_summary, indent=2)},
        ],
        temperature=0.3,
        max_tokens=400,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "current_leader": narrative_summary[0]["name"] if narrative_summary else "Unknown",
            "rotation_target": narrative_summary[-1]["name"] if narrative_summary else "Unknown",
            "rotation_confidence": 0.5,
            "rotation_trigger": "Volume decline in current leader",
            "estimated_rotation_days": 14,
            "reasoning": "Fallback rotation prediction based on lifecycle stages.",
            "watchlist": [n["name"] for n in narrative_summary[1:3]],
        }

    return result


if __name__ == "__main__":
    from classify_lifecycle import classify_all

    print("Running classification pipeline...")
    classifications, global_context = classify_all(top_n=5)

    print("\nPredicting narrative rotation...\n")
    rotation = predict_rotation(classifications)

    print("=" * 65)
    print("NARRATIVE ROTATION FORECAST")
    print("=" * 65)
    print(f"Current Leader       : {rotation['current_leader']}")
    print(f"Rotation Target      : {rotation['rotation_target']}")
    print(f"Rotation Confidence  : {round(rotation['rotation_confidence'] * 100)}%")
    print(f"Estimated Days       : {rotation['estimated_rotation_days']}")
    print(f"Trigger              : {rotation['rotation_trigger']}")
    print(f"Reasoning            : {rotation['reasoning']}")
    print(f"Watchlist            : {rotation['watchlist']}")