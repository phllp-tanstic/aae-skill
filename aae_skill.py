"""
Attention Arbitrage Engine (AAE)
=================================
A CMC Skill that detects narrative velocity divergence
and generates backtestable crypto trading strategies
using AI lifecycle classification.

BNB x CMC Hackathon — Track 2
"""

import json
from datetime import datetime
from generate_strategy import generate_all_specs


def run_aae(top_n=5, save_output=True):
    """
    Master entry point for the Attention Arbitrage Engine.

    Runs the full pipeline:
    1. Fetch trending narratives from CMC
    2. Score velocity (attention vs price divergence)
    3. Check divergence signal strength
    4. Enrich with macro regime context
    5. Classify lifecycle stage with AI
    6. Generate backtestable strategy specifications

    Returns list of strategy specs sorted by opportunity score.
    """

    print()
    print("=" * 65)
    print("  ATTENTION ARBITRAGE ENGINE v1.0")
    print("  BNB x CMC Hackathon — Track 2")
    print(f"  Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print()

    specs, global_context = generate_all_specs(top_n=top_n)

    print()
    print("=" * 65)
    print("AAE FINAL OUTPUT — STRATEGY SPECIFICATIONS")
    print("=" * 65)
    print(f"Regime    : {global_context['regime']}")
    print(f"BTC Dom   : {global_context['btc_dominance']}%")
    print(f"Specs gen : {len(specs)}")
    print(f"Timestamp : {datetime.now().isoformat()}")
    print()

    for i, spec in enumerate(specs, 1):
        stage_emoji = {
            "EMERGENCE": "🟢",
            "ACCELERATION": "🟡",
            "SATURATION": "🟠",
            "DECAY": "🔴"
        }.get(spec["lifecycle_stage"], "⚪")

        print(f"{i}. {stage_emoji}  {spec['narrative']}")
        print(f"   Stage      : {spec['lifecycle_stage']}")
        print(f"   Opportunity: {spec['opportunity_score']} / 100")
        print(f"   Confidence : {round(spec['confidence'] * 100)}%")
        print(f"   Risk       : {spec['risk_level']}")
        print(f"   Strategy   : {spec['strategy']['type']}")
        print(f"   Entry      : {spec['strategy']['entry_trigger']}")
        print(f"   Stop Loss  : {spec['strategy']['stop_loss']}")
        print(f"   Horizon    : {spec['strategy']['time_horizon']}")
        print(f"   Assets     : {spec['backtestable_assets']}")
        print(f"   Spec ID    : {spec['spec_id']}")
        print()

    if save_output:
        filename = f"aae_output_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, "w") as f:
            json.dump({
                "engine": "Attention Arbitrage Engine v1.0",
                "generated_at": datetime.now().isoformat(),
                "market_context": global_context,
                "strategy_specs": specs,
            }, f, indent=2)
        print(f"Full output saved to: {filename}")

    return specs


if __name__ == "__main__":
    specs = run_aae(top_n=5)
    print()
    print("AAE run complete.")
    print(f"Top opportunity: {specs[0]['narrative']} [{specs[0]['lifecycle_stage']}]")