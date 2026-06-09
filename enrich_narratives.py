import requests
from dotenv import load_dotenv
from check_divergence import run_divergence_check
import os

load_dotenv()

api_key = os.getenv("CMC_API_KEY")
headers = {"X-CMC_PRO_API_KEY": api_key}
BASE = "https://pro-api.coinmarketcap.com"


def fetch_global_context():
    """
    Fetch global market context.
    Used to understand macro regime for all narratives.
    """
    url = f"{BASE}/v1/global-metrics/quotes/latest"
    r = requests.get(url, headers=headers)
    data = r.json().get("data", {})

    btc_dominance = round(data.get("btc_dominance", 0), 2)
    eth_dominance = round(data.get("eth_dominance", 0), 2)
    total_mcap = data.get("quote", {}).get("USD", {}).get("total_market_cap", 0)
    total_volume = data.get("quote", {}).get("USD", {}).get("total_volume_24h", 0)
    mcap_change = round(data.get("quote", {}).get("USD", {}).get("total_market_cap_yesterday_percentage_change", 0), 2)

    if btc_dominance > 58:
        regime = "BTC_DOMINANCE"
        regime_note = "Capital concentrated in BTC — altcoin narratives face headwind"
    elif btc_dominance < 45:
        regime = "ALTCOIN_SEASON"
        regime_note = "BTC dominance low — narrative plays have tailwind"
    else:
        regime = "NEUTRAL"
        regime_note = "Balanced market — narrative signals carry normal weight"

    return {
        "btc_dominance": btc_dominance,
        "eth_dominance": eth_dominance,
        "total_market_cap": total_mcap,
        "total_volume_24h": total_volume,
        "mcap_change_24h": mcap_change,
        "regime": regime,
        "regime_note": regime_note,
    }


def fetch_token_derivatives(symbol):
    """
    Fetch derivatives data for a token symbol.
    Returns funding rate and open interest if available.
    """
    url = f"{BASE}/v1/cryptocurrency/quotes/latest"
    params = {"symbol": symbol, "aux": "volume_7d,volume_30d"}
    r = requests.get(url, headers=headers, params=params)
    data = r.json().get("data", {})

    if not data or symbol not in data:
        return None

    token_data = data[symbol]
    if isinstance(token_data, list):
        token_data = token_data[0]

    quote = token_data.get("quote", {}).get("USD", {})

    return {
        "symbol": symbol,
        "volume_7d": round(quote.get("volume_7d") or 0, 0),
        "volume_30d": round(quote.get("volume_30d") or 0, 0),
        "change_7d": round(quote.get("percent_change_7d") or 0, 2),
        "change_30d": round(quote.get("percent_change_30d") or 0, 2),
        "market_cap": round(quote.get("market_cap") or 0, 0),
    }


def enrich_narrative(divergence_result, global_context):
    """
    Takes a divergence result and adds:
    - Global macro regime context
    - Token-level volume trend (7d vs 24h)
    - Enriched signal strength
    """
    tokens = divergence_result.get("tokens", [])
    enriched_tokens = []

    for t in tokens[:3]:
        symbol = t.get("symbol", "")
        deriv = fetch_token_derivatives(symbol)

        token_enriched = {**t}

        if deriv:
            vol_acceleration = "accelerating" if deriv["volume_7d"] > 0 else "flat"
            token_enriched["volume_7d"] = deriv["volume_7d"]
            token_enriched["change_30d"] = deriv["change_30d"]
            token_enriched["volume_trend"] = vol_acceleration

        enriched_tokens.append(token_enriched)

    regime = global_context["regime"]
    stage = divergence_result["stage_hint"]
    signal = divergence_result["signal"]

    if regime == "ALTCOIN_SEASON" and "STRONG" in signal:
        adjusted_signal = "HIGH CONVICTION — strong divergence in altcoin-favorable regime"
    elif regime == "BTC_DOMINANCE" and "STRONG" in signal:
        adjusted_signal = "MODERATE CONVICTION — strong divergence but BTC dominance headwind"
    elif regime == "NEUTRAL" and "STRONG" in signal:
        adjusted_signal = "SOLID CONVICTION — strong divergence in neutral regime"
    else:
        adjusted_signal = signal

    return {
        **divergence_result,
        "tokens": enriched_tokens,
        "global_regime": regime,
        "regime_note": global_context["regime_note"],
        "adjusted_signal": adjusted_signal,
        "btc_dominance": global_context["btc_dominance"],
    }


def run_enrichment(top_n=5):
    """
    Full enrichment pipeline:
    fetch → score → divergence → enrich
    """
    print("Fetching global market context...")
    global_context = fetch_global_context()
    print(f"  Regime: {global_context['regime']}")
    print(f"  BTC Dominance: {global_context['btc_dominance']}%")
    print(f"  Note: {global_context['regime_note']}")
    print()

    print("Running divergence analysis...")
    divergence_results = run_divergence_check(top_n=top_n)

    print("\nEnriching narratives with macro context...\n")
    enriched = []
    for result in divergence_results:
        e = enrich_narrative(result, global_context)
        enriched.append(e)

    return enriched, global_context


if __name__ == "__main__":
    enriched, global_context = run_enrichment(top_n=5)

    print("\n" + "=" * 65)
    print("ENRICHED NARRATIVE INTELLIGENCE REPORT")
    print("=" * 65)
    print(f"Market Regime: {global_context['regime']}")
    print(f"BTC Dominance: {global_context['btc_dominance']}%")
    print()

    for i, n in enumerate(enriched, 1):
        print(f"{i}. {n['name']}")
        print(f"   Velocity Score : {n['velocity_score']} / 100")
        print(f"   Lifecycle Stage: {n['stage_hint']}")
        print(f"   Signal         : {n['adjusted_signal']}")
        print(f"   Regime Impact  : {n['regime_note']}")
        print(f"   Top Tokens:")
        for t in n["tokens"]:
            trend = t.get("volume_trend", "unknown")
            print(f"     {t['symbol']:<8} 24h: {t['change_24h']}%  7d: {t['change_7d']}%  volume trend: {trend}")
        print()

    print("Enrichment complete.")