import requests
from dotenv import load_dotenv
from fetch_narratives import fetch_narratives
import os

load_dotenv()

api_key = os.getenv("CMC_API_KEY")
headers = {"X-CMC_PRO_API_KEY": api_key}
BASE = "https://pro-api.coinmarketcap.com"


def fetch_market_growth():
    """
    Fetch BTC 24h volume change as baseline for relative alpha.
    CMC global metrics returns 0 for total_volume_24h_yesterday_percentage_change,
    so we use BTC as the market proxy instead — it is always non-zero.
    """
    url = f"{BASE}/v1/cryptocurrency/quotes/latest"
    params = {"symbol": "BTC"}
    r = requests.get(url, headers=headers, params=params)
    data = r.json().get("data", {})

    btc_data = data.get("BTC", [])
    if isinstance(btc_data, list):
        btc_data = btc_data[0]

    quote = btc_data.get("quote", {}).get("USD", {})
    btc_vol_change = quote.get("volume_change_24h", 0) or 0

    return round(btc_vol_change, 2)


def score_velocity(narrative, market_volume_change=0):
    """
    Computes a velocity score 0-100 for a narrative.
    High score = attention growing faster than price.

    Components:
    - Volume surge score (40 points max)
    - Market cap momentum score (30 points max)
    - Divergence bonus: volume >> price (30 points max)

    Also computes relative_attention_alpha:
    How much faster this narrative is growing vs BTC volume baseline.
    """
    vol_change = narrative["volume_change_24h"]
    mcap_change = narrative["market_cap_change_24h"]
    price_change = narrative["avg_change_24h"]

    vol_score = min(40, (vol_change / 100) * 40)
    vol_score = max(0, vol_score)

    mcap_score = min(30, (mcap_change / 20) * 30)
    mcap_score = max(0, mcap_score)

    divergence = vol_change - abs(price_change)
    divergence_score = min(30, (divergence / 80) * 30)
    divergence_score = max(0, divergence_score)

    total = round(vol_score + mcap_score + divergence_score, 2)

    # Relative alpha: how much faster this narrative grows vs BTC volume baseline
    relative_attention_alpha = round(vol_change - market_volume_change, 2)

    return {
        "name": narrative["name"],
        "velocity_score": total,
        "vol_score": round(vol_score, 2),
        "mcap_score": round(mcap_score, 2),
        "divergence_score": round(divergence_score, 2),
        "avg_change_24h": narrative["avg_change_24h"],
        "volume_change_24h": narrative["volume_change_24h"],
        "market_cap_change_24h": narrative["market_cap_change_24h"],
        "num_tokens": narrative["num_tokens"],
        "market_volume_change": market_volume_change,
        "relative_attention_alpha": relative_attention_alpha,
    }


def score_all_narratives(limit=10):
    """Fetch narratives and score them all, sorted by velocity."""
    narratives = fetch_narratives(limit)
    market_vol_change = fetch_market_growth()
    scored = [score_velocity(n, market_vol_change) for n in narratives]
    scored.sort(key=lambda x: x["velocity_score"], reverse=True)
    return scored


if __name__ == "__main__":
    print("Scoring narrative velocity...\n")
    scored = score_all_narratives(10)

    print(f"BTC baseline volume change: {scored[0]['market_volume_change']}%\n")
    print(f"{'Rank':<5} {'Narrative':<30} {'Score':<8} {'Vol':<8} {'Alpha':<10}")
    print("-" * 65)

    for i, n in enumerate(scored, 1):
        print(
            f"{i:<5} "
            f"{n['name']:<30} "
            f"{n['velocity_score']:<8} "
            f"{n['vol_score']:<8} "
            f"{n['relative_attention_alpha']:<10}"
        )

    print()
    print("Top narrative by velocity:", scored[0]["name"])
    print("Relative attention alpha:", scored[0]["relative_attention_alpha"], "%")