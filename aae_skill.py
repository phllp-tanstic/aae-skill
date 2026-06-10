"""
Attention Arbitrage Engine (AAE) v2.0
=======================================
An AI-powered narrative intelligence system that detects
attention-price divergence, classifies lifecycle stage,
predicts narrative half-life, forecasts rotation, and
generates backtestable trading strategies before market
consensus forms.

BNB x CMC Hackathon — Track 2
GitHub: github.com/phllp-tanstic/aae-skill

Stack:
- CoinMarketCap Agent Hub (REST API + MCP + Skill Hub)
- BNB AI Agent SDK (ERC-8004 on-chain identity)
- Trust Wallet Agent Kit (self-custody signing + price feeds)
"""

import json
from datetime import datetime
from classify_lifecycle import classify_all
from generate_strategy import generate_strategy_spec
from predict_rotation import predict_rotation


STAGE_EMOJI = {
    "EMERGENCE": "🟢",
    "EARLY_ACCELERATION": "🟡",
    "LATE_ACCELERATION": "🟠",
    "SATURATION": "🔴",
    "DECAY": "⚫",
}


def print_dashboard(enriched, classification):
    """Print narrative intelligence dashboard for one narrative."""
    c = classification
    e = enriched
    stage = c.get("lifecycle_stage", "EMERGENCE")
    emoji = STAGE_EMOJI.get(stage, "⚪")
    analog = c.get("historical_analog", {})

    print(f"\n{'─'*65}")
    print(f"  {emoji}  NARRATIVE: {c['narrative_name'].upper()}")
    print(f"{'─'*65}")
    print(f"  Lifecycle Stage      : {stage}")
    print(f"  Attention Score      : {e.get('velocity_score', 0)} / 100")
    print(f"  Relative Alpha       : +{e.get('relative_attention_alpha', 0)}% vs market")
    print(f"  Price Confirmation   : {abs(e.get('avg_change_24h', 0))}%")
    print(f"  Opportunity Score    : {c.get('opportunity_score', 0)} / 100")
    print(f"  Confidence           : {round(c.get('confidence', 0) * 100)}%")
    print(f"  Risk Level           : {c.get('risk_level', 'MEDIUM')}")
    print(f"  Narrative Half-Life  : ~{c.get('estimated_half_life_days', 'N/A')} days")
    print(f"  Decay Probability    : {round(c.get('attention_decay_probability', 0) * 100)}%")
    print()
    print(f"  Historical Analog    : {analog.get('match', 'N/A')}")
    print(f"  Similarity           : {round(analog.get('similarity_score', 0) * 100)}%")
    print(f"  Analog Insight       : {analog.get('insight', 'N/A')}")
    print()
    print(f"  AI Reasoning:")
    for point in c.get("reasoning", []):
        print(f"    • {point}")
    print()


def run_aae(top_n=5, save_output=True):
    """
    Master entry point for the Attention Arbitrage Engine.

    Single-pass pipeline (no duplicate API calls):
    1. fetch_narratives     → CMC /v1/cryptocurrency/categories
    2. score_velocity       → CMC /v1/global-metrics/quotes/latest
    3. check_divergence     → CMC /v1/cryptocurrency/category
    4. enrich_narratives    → CMC /v1/cryptocurrency/quotes/latest
    5. classify_lifecycle   → Groq LLaMA 3.3 70B (AI reasoning)
    6. predict_rotation     → Groq LLaMA 3.3 70B (rotation forecast)
    7. generate_strategy    → Rule-based spec from lifecycle stage
    8. Save output          → JSON strategy spec file
    """

    print()
    print("=" * 65)
    print("  ATTENTION ARBITRAGE ENGINE v2.0")
    print("  Narrative Intelligence Platform")
    print("  BNB x CMC Hackathon — Track 2")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 65)
    print()

    # Step 1-5: Full enrichment + AI classification (single pipeline pass)
    classifications, global_context = classify_all(top_n=top_n)

    # Step 6: Generate strategy specs from classifications
    specs = []
    for result in classifications:
        spec = generate_strategy_spec(result, global_context)
        specs.append(spec)
    specs.sort(key=lambda x: x["opportunity_score"], reverse=True)

    # Save base strategy output for backtester and integrations
    with open("strategy_output.json", "w") as f:
        json.dump(specs, f, indent=2)

    # Step 7: Narrative rotation forecast
    rotation = predict_rotation(classifications)

    # Display narrative intelligence dashboard
    print()
    print("=" * 65)
    print("  NARRATIVE INTELLIGENCE DASHBOARD")
    print("=" * 65)
    print(f"  Market Regime : {global_context['regime']}")
    print(f"  BTC Dominance : {global_context['btc_dominance']}%")
    print(f"  Regime Note   : {global_context['regime_note']}")

    for item in classifications:
        print_dashboard(item["enriched"], item["classification"])

    # Display rotation forecast
    print()
    print("=" * 65)
    print("  NARRATIVE ROTATION FORECAST")
    print("=" * 65)
    print(f"  Current Leader    : {rotation['current_leader']}")
    print(f"  Rotation Target   : {rotation['rotation_target']}")
    print(f"  Confidence        : {round(rotation['rotation_confidence'] * 100)}%")
    print(f"  Est. Days         : {rotation['estimated_rotation_days']}")
    print(f"  Trigger           : {rotation['rotation_trigger']}")
    print(f"  Reasoning         : {rotation['reasoning']}")
    print(f"  Watchlist         : {rotation['watchlist']}")

    # Display strategy specifications
    print()
    print("=" * 65)
    print("  STRATEGY SPECIFICATIONS")
    print("=" * 65)

    for i, spec in enumerate(specs, 1):
        stage = spec["lifecycle_stage"]
        emoji = STAGE_EMOJI.get(stage, "⚪")
        print(f"\n  {i}. {emoji}  {spec['narrative']}  [{stage}]")
        print(f"     Spec ID    : {spec['spec_id']}")
        print(f"     Opportunity: {spec['opportunity_score']} / 100")
        print(f"     Strategy   : {spec['strategy']['type']}")
        print(f"     Entry      : {spec['strategy']['entry_trigger']}")
        print(f"     Stop Loss  : {spec['strategy']['stop_loss']}")
        print(f"     Horizon    : {spec['strategy']['time_horizon']}")
        print(f"     Assets     : {spec['backtestable_assets']}")

    # Save full output
    if save_output:
        filename = f"aae_output_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        output = {
            "engine": "Attention Arbitrage Engine v2.0",
            "generated_at": datetime.now().isoformat(),
            "market_context": global_context,
            "rotation_forecast": rotation,
            "strategy_specs": specs,
        }
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n  Full output saved to: {filename}")

    print()
    print("=" * 65)
    print(f"  AAE run complete.")
    print(f"  Top opportunity : {specs[0]['narrative']} [{specs[0]['lifecycle_stage']}]")
    print(f"  Rotation target : {rotation['rotation_target']}")
    print("=" * 65)

    return specs, rotation


if __name__ == "__main__":
    run_aae(top_n=5)