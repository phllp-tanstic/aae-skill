import json
from datetime import datetime
from classify_lifecycle import classify_all


STRATEGY_TEMPLATES = {
    "EMERGENCE": {
        "strategy_type": "Early Position Accumulation",
        "thesis": "Narrative attention is accelerating faster than price. Accumulate before mainstream discovery.",
        "entry_rule": "Enter when velocity_score > 60 AND volume_change_24h > 100% AND avg_price_change_24h < 15%",
        "entry_trigger": "Buy on next daily open after signal confirmation",
        "position_size": "2-4% of portfolio per narrative (high risk, early stage)",
        "exit_rule_profit": "Exit 50% position at +40% price gain, trail stop on remainder",
        "exit_rule_time": "Exit full position if velocity_score drops below 40 within 14 days",
        "stop_loss": "-15% from entry price",
        "time_horizon": "7-21 days",
        "max_drawdown_tolerance": "15%",
        "notes": "Split entry into 3 tranches over 48 hours to reduce timing risk",
    },
    "ACCELERATION": {
        "strategy_type": "Momentum Ride",
        "thesis": "Narrative is confirmed and gaining mainstream traction. Ride the momentum with tight risk management.",
        "entry_rule": "Enter when velocity_score 35-60 AND both volume AND price trending up AND global_regime != BTC_DOMINANCE",
        "entry_trigger": "Buy on pullback to 10-day moving average or volume confirmation",
        "position_size": "3-5% of portfolio per narrative (medium risk, confirmed trend)",
        "exit_rule_profit": "Exit 33% at +25%, 33% at +50%, trail stop on final 33%",
        "exit_rule_time": "Exit if volume_change_24h drops below 10% for 3 consecutive days",
        "stop_loss": "-10% from entry price",
        "time_horizon": "5-14 days",
        "max_drawdown_tolerance": "10%",
        "notes": "Reduce position size by 50% if BTC_DOMINANCE regime detected",
    },
    "SATURATION": {
        "strategy_type": "Fade the Narrative",
        "thesis": "Narrative is widely known and priced in. Risk/reward favors reduction or short exposure.",
        "entry_rule": "Enter short when velocity_score < 30 AND price_change > 50% over 7 days AND volume declining",
        "entry_trigger": "Short on first red daily candle after 3+ consecutive green days",
        "position_size": "1-2% of portfolio (contrarian, use only with conviction)",
        "exit_rule_profit": "Cover short at -20% price decline from entry",
        "exit_rule_time": "Cover short after 7 days regardless of P&L",
        "stop_loss": "+8% from short entry price",
        "time_horizon": "3-10 days",
        "max_drawdown_tolerance": "8%",
        "notes": "Only execute in NEUTRAL or ALTCOIN_SEASON regime — avoid shorting in BTC_DOMINANCE",
    },
    "DECAY": {
        "strategy_type": "Capital Rotation Exit",
        "thesis": "Narrative momentum exhausted. Rotate capital to higher-velocity opportunities.",
        "entry_rule": "No new long entries. If holding, exit on next volume spike above 30-day average.",
        "entry_trigger": "No entry. Exit only.",
        "position_size": "0% new allocation",
        "exit_rule_profit": "Exit all remaining positions within 48 hours",
        "exit_rule_time": "Immediate exit",
        "stop_loss": "N/A — exit position",
        "time_horizon": "Exit within 1-3 days",
        "max_drawdown_tolerance": "0% — capital preservation mode",
        "notes": "Rotate freed capital to any EMERGENCE narrative with velocity_score > 60",
    },
}


def generate_strategy_spec(classification_result, global_context):
    enriched = classification_result["enriched"]
    classification = classification_result["classification"]
    stage = classification["lifecycle_stage"]
    template = STRATEGY_TEMPLATES.get(stage, STRATEGY_TEMPLATES["ACCELERATION"])
    tokens = enriched.get("tokens", [])
    token_symbols = [t["symbol"] for t in tokens if t.get("symbol")]

    if stage == "EMERGENCE" and global_context["regime"] == "BTC_DOMINANCE":
        confidence_adjusted = round(classification["confidence"] * 0.85, 2)
        size_note = "REDUCE position size by 30% due to BTC dominance headwind"
    elif stage == "ACCELERATION" and global_context["regime"] == "ALTCOIN_SEASON":
        confidence_adjusted = round(min(classification["confidence"] * 1.1, 1.0), 2)
        size_note = "INCREASE position size by 20% — altcoin season tailwind"
    else:
        confidence_adjusted = classification["confidence"]
        size_note = "Standard position sizing applies"

    spec = {
        "spec_id": f"AAE-{datetime.now().strftime('%Y%m%d-%H%M')}-{stage[:3]}",
        "generated_at": datetime.now().isoformat(),
        "engine": "Attention Arbitrage Engine v2.0",
        "narrative": classification["narrative_name"],
        "lifecycle_stage": stage,
        "confidence": confidence_adjusted,
        "opportunity_score": classification["opportunity_score"],
        "risk_level": classification["risk_level"],
        "ai_reasoning": classification["reasoning"],
        "estimated_half_life_days": classification.get("estimated_half_life_days"),
        "attention_decay_probability": classification.get("attention_decay_probability"),
        "historical_analog": classification.get("historical_analog", {}),
        "market_context": {
            "regime": global_context["regime"],
            "btc_dominance": global_context["btc_dominance"],
            "regime_note": global_context["regime_note"],
        },
        "signal_data": {
            "velocity_score": enriched["velocity_score"],
            "volume_change_24h": enriched["volume_change_24h"],
            "avg_price_change_24h": enriched["avg_change_24h"],
            "divergence_signal": enriched["adjusted_signal"],
        },
        "strategy": {
            "type": template["strategy_type"],
            "thesis": template["thesis"],
            "entry_rule": template["entry_rule"],
            "entry_trigger": template["entry_trigger"],
            "position_size": template["position_size"],
            "position_size_adjustment": size_note,
            "exit_rule_profit": template["exit_rule_profit"],
            "exit_rule_time": template["exit_rule_time"],
            "stop_loss": template["stop_loss"],
            "time_horizon": template["time_horizon"],
            "max_drawdown_tolerance": template["max_drawdown_tolerance"],
            "notes": template["notes"],
        },
        "backtestable_assets": token_symbols,
        "backtest_parameters": {
            "lookback_window": "30 days",
            "entry_on": "daily open",
            "benchmark": "BTC",
            "fee_assumption": "0.1% per trade",
        },
    }

    return spec


def generate_all_specs(top_n=5):
    print("Running full AAE pipeline...\n")
    classifications, global_context = classify_all(top_n=top_n)

    print("\nGenerating strategy specifications...\n")
    specs = []

    for result in classifications:
        spec = generate_strategy_spec(result, global_context)
        specs.append(spec)
        print(f"  Generated spec: {spec['spec_id']} — {spec['narrative']} [{spec['lifecycle_stage']}]")

    specs.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return specs, global_context


if __name__ == "__main__":
    specs, global_context = generate_all_specs(top_n=5)

    print("\n" + "=" * 65)
    print("ATTENTION ARBITRAGE ENGINE — STRATEGY SPECIFICATIONS")
    print("=" * 65)

    for i, spec in enumerate(specs, 1):
        print(f"\n{'='*65}")
        print(f"SPEC #{i}: {spec['spec_id']}")
        print(f"{'='*65}")
        print(f"Narrative        : {spec['narrative']}")
        print(f"Lifecycle Stage  : {spec['lifecycle_stage']}")
        print(f"Confidence       : {round(spec['confidence'] * 100)}%")
        print(f"Opportunity Score: {spec['opportunity_score']} / 100")
        print(f"Risk Level       : {spec['risk_level']}")
        print()
        print(f"STRATEGY: {spec['strategy']['type']}")
        print(f"Thesis   : {spec['strategy']['thesis']}")
        print()
        print(f"Entry Rule : {spec['strategy']['entry_rule']}")
        print(f"Entry Trigger : {spec['strategy']['entry_trigger']}")
        print(f"Position Size : {spec['strategy']['position_size']}")
        print(f"Size Adjustment: {spec['strategy']['position_size_adjustment']}")
        print()
        print(f"Profit Exit : {spec['strategy']['exit_rule_profit']}")
        print(f"Time Exit   : {spec['strategy']['exit_rule_time']}")
        print(f"Stop Loss   : {spec['strategy']['stop_loss']}")
        print(f"Time Horizon: {spec['strategy']['time_horizon']}")
        print()
        print(f"Assets to backtest: {spec['backtestable_assets']}")
        print(f"AI Reasoning: {spec['ai_reasoning']}")

    print(f"\n\nTotal specs generated: {len(specs)}")
    print("Saving specs to strategy_output.json...")

    with open("strategy_output.json", "w") as f:
        json.dump(specs, f, indent=2)

    print("Saved to strategy_output.json")