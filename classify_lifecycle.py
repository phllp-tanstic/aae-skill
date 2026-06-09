import os
import json
from groq import Groq
from dotenv import load_dotenv
from enrich_narratives import run_enrichment

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are the AI core of the Attention Arbitrage Engine — a narrative intelligence system for crypto markets.

Your job is to analyze enriched narrative data and return a structured JSON classification.

Lifecycle stages:
EMERGENCE — Volume surging, price flat. Very early. High opportunity, high risk.
EARLY_ACCELERATION — Momentum building. Volume and price both starting to move.
LATE_ACCELERATION — Mainstream traction. Strong price action, volume still high.
SATURATION — Widely known. Price moved significantly. Diminishing returns.
DECAY — Momentum exhausted. Volume and price declining.

Narrative Half-Life definition:
Estimated days until narrative attention falls by 50%.
Use these reference points:
- Memecoins: 7-14 days
- Exchange/launchpad narratives: 14-30 days
- DeFi/yield narratives: 30-60 days
- Infrastructure/L2 narratives: 60-120 days
- RWA/institutional narratives: 90-180 days

Historical Analog Matching:
Match the current narrative pattern to the closest historical crypto narrative event.
Examples: DeFi Summer 2020, NFT Boom 2021, L2 Race 2022, AI Agent Surge 2024,
Memecoin Supercycle 2024, LSDfi Emergence 2023, RWA Narrative 2023.

Respond ONLY with valid JSON, no other text:
{
  "narrative_name": "string",
  "lifecycle_stage": "EMERGENCE|EARLY_ACCELERATION|LATE_ACCELERATION|SATURATION|DECAY",
  "confidence": 0.0,
  "reasoning": [
    "specific data-driven observation 1",
    "specific data-driven observation 2",
    "specific data-driven observation 3"
  ],
  "opportunity_score": 0,
  "risk_level": "LOW|MEDIUM|HIGH|EXTREME",
  "estimated_half_life_days": 0,
  "attention_decay_probability": 0.0,
  "historical_analog": {
    "match": "name of closest historical narrative",
    "similarity_score": 0.0,
    "insight": "one sentence explaining what this analog predicts"
  }
}"""


def classify_narrative(enriched_narrative):
    narrative_input = {
        "narrative_name": enriched_narrative.get("name"),
        "velocity_score": enriched_narrative.get("velocity_score"),
        "volume_change_24h": enriched_narrative.get("volume_change_24h"),
        "avg_change_24h": enriched_narrative.get("avg_change_24h"),
        "market_cap_change_24h": enriched_narrative.get("market_cap_change_24h", 0),
        "relative_attention_alpha": enriched_narrative.get("relative_attention_alpha", 0),
        "stage_hint": enriched_narrative.get("stage_hint"),
        "adjusted_signal": enriched_narrative.get("adjusted_signal"),
        "global_regime": enriched_narrative.get("global_regime"),
        "regime_note": enriched_narrative.get("regime_note"),
        "btc_dominance": enriched_narrative.get("btc_dominance"),
        "num_tokens": enriched_narrative.get("num_tokens", 0),
        "tokens": enriched_narrative.get("tokens", []),
    }

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(narrative_input, indent=2)},
        ],
        temperature=0.2,
        max_tokens=600,
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
            "narrative_name": enriched_narrative.get("name"),
            "lifecycle_stage": "EMERGENCE",
            "confidence": 0.5,
            "reasoning": [
                "Fallback classification — AI response could not be parsed.",
                f"Velocity score: {enriched_narrative.get('velocity_score')}",
                f"Volume change: {enriched_narrative.get('volume_change_24h')}%",
            ],
            "opportunity_score": enriched_narrative.get("velocity_score", 50),
            "risk_level": "MEDIUM",
            "estimated_half_life_days": 30,
            "attention_decay_probability": 0.5,
            "historical_analog": {
                "match": "Unknown",
                "similarity_score": 0.0,
                "insight": "No analog available.",
            },
        }

    return result


def classify_all(top_n=5):
    print("Running full enrichment pipeline...")
    enriched, global_context = run_enrichment(top_n=top_n)

    print("\nClassifying lifecycle stages with AI...\n")
    classifications = []

    for narrative in enriched:
        print(f"  Classifying: {narrative['name']}...")
        result = classify_narrative(narrative)
        classifications.append({
            "enriched": narrative,
            "classification": result,
        })

    return classifications, global_context


if __name__ == "__main__":
    results, global_context = classify_all(top_n=5)

    print("\n" + "=" * 65)
    print("AI NARRATIVE INTELLIGENCE RESULTS")
    print("=" * 65)
    print(f"Market Regime: {global_context['regime']}")
    print(f"BTC Dominance: {global_context['btc_dominance']}%")
    print()

    for r in results:
        c = r["classification"]
        e = r["enriched"]
        print(f"Narrative      : {c['narrative_name']}")
        print(f"Lifecycle Stage: {c['lifecycle_stage']}")
        print(f"Confidence     : {round(c['confidence'] * 100)}%")
        print(f"Opportunity    : {c['opportunity_score']} / 100")
        print(f"Risk Level     : {c['risk_level']}")
        print(f"Half-Life Est  : {c.get('estimated_half_life_days', 'N/A')} days")
        print(f"Decay Prob     : {c.get('attention_decay_probability', 'N/A')}")
        analog = c.get("historical_analog", {})
        print(f"Historical Match: {analog.get('match')} (similarity: {analog.get('similarity_score')})")
        print(f"Analog Insight : {analog.get('insight')}")
        print(f"AI Reasoning:")
        for point in c.get("reasoning", []):
            print(f"  • {point}")
        print()

    print("Classification complete.")