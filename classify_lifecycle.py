import os
import json
from groq import Groq
from dotenv import load_dotenv
from enrich_narratives import run_enrichment

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a crypto narrative lifecycle classifier for the Attention Arbitrage Engine.

Your job is to analyze enriched narrative data and classify each narrative into exactly one of four lifecycle stages:

EMERGENCE - Narrative is just appearing. Volume surging but price flat. Very early signal. High opportunity, high risk.
ACCELERATION - Narrative gaining mainstream attention. Both volume and price rising. Good risk/reward window.
SATURATION - Narrative widely known. Price already moved significantly. Late entry, diminishing returns.
DECAY - Narrative losing momentum. Volume dropping, price declining. Avoid or short.

You will receive a JSON object with narrative data including:
- velocity_score (0-100)
- volume_change_24h (%)
- avg_change_24h (price %)
- market_cap_change_24h (%)
- stage_hint (preliminary rule-based classification)
- adjusted_signal (signal strength)
- global_regime (BTC_DOMINANCE / ALTCOIN_SEASON / NEUTRAL)
- token data (24h and 7d price changes)

Respond ONLY with a valid JSON object in this exact format, no other text:
{
  "narrative_name": "name here",
  "lifecycle_stage": "EMERGENCE or ACCELERATION or SATURATION or DECAY",
  "confidence": 0.0 to 1.0,
  "reasoning": "2-3 sentences explaining why",
  "opportunity_score": 0 to 100,
  "risk_level": "LOW or MEDIUM or HIGH or EXTREME"
}"""


def classify_narrative(enriched_narrative):
    narrative_input = {
        "narrative_name": enriched_narrative.get("name"),
        "velocity_score": enriched_narrative.get("velocity_score"),
        "volume_change_24h": enriched_narrative.get("volume_change_24h"),
        "avg_change_24h": enriched_narrative.get("avg_change_24h"),
        "market_cap_change_24h": enriched_narrative.get("market_cap_change_24h", 0),
        "stage_hint": enriched_narrative.get("stage_hint"),
        "adjusted_signal": enriched_narrative.get("adjusted_signal"),
        "global_regime": enriched_narrative.get("global_regime"),
        "regime_note": enriched_narrative.get("regime_note"),
        "btc_dominance": enriched_narrative.get("btc_dominance"),
        "tokens": enriched_narrative.get("tokens", []),
    }

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(narrative_input, indent=2)},
        ],
        temperature=0.2,
        max_tokens=400,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "narrative_name": enriched_narrative.get("name"),
            "lifecycle_stage": "EMERGENCE",
            "confidence": 0.5,
            "reasoning": "Fallback to rule-based classification.",
            "opportunity_score": enriched_narrative.get("velocity_score", 50),
            "risk_level": "MEDIUM",
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
    print("AI LIFECYCLE CLASSIFICATION RESULTS")
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
        print(f"Reasoning      : {c['reasoning']}")
        print(f"Velocity Score : {e['velocity_score']} / 100")
        print()

    print("Classification complete.")