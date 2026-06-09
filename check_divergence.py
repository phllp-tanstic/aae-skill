import requests
from dotenv import load_dotenv
from score_velocity import score_all_narratives
import os

load_dotenv()

api_key = os.getenv("CMC_API_KEY")
headers = {"X-CMC_PRO_API_KEY": api_key}
BASE = "https://pro-api.coinmarketcap.com"


def fetch_category_tokens(category_name, limit=5):
    """
    Fetch top tokens inside a narrative category.
    Returns list of tokens with price and volume data.
    """
    url = f"{BASE}/v1/cryptocurrency/categories"
    params = {"limit": 50}
    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    category_id = None
    for cat in data.get("data", []):
        if cat["name"] == category_name:
            category_id = cat["id"]
            break

    if not category_id:
        return []

    url2 = f"{BASE}/v1/cryptocurrency/category"
    params2 = {"id": category_id, "limit": limit}
    r2 = requests.get(url2, headers=headers, params=params2)
    data2 = r2.json()

    tokens = []
    for coin in data2.get("data", {}).get("coins", []):
        quote = coin.get("quote", {}).get("USD", {})
        tokens.append({
            "name": coin.get("name"),
            "symbol": coin.get("symbol"),
            "price": round(quote.get("price") or 0, 4),
            "change_24h": round(quote.get("percent_change_24h") or 0, 2),
            "change_7d": round(quote.get("percent_change_7d") or 0, 2),
            "volume_24h": round(quote.get("volume_24h") or 0, 0),
            "market_cap": round(quote.get("market_cap") or 0, 0),
        })

    return tokens


def compute_divergence_signal(narrative_name, velocity_score, volume_change, price_change):
    """
    Classifies the divergence signal strength.
    High volume surge + low price = strong early signal.
    """
    gap = volume_change - abs(price_change)

    if gap > 100 and velocity_score > 60:
        signal = "STRONG — price hasn't caught up to attention yet"
        stage_hint = "Emergence"
    elif gap > 50 and velocity_score > 40:
        signal = "MODERATE — early momentum building"
        stage_hint = "Early Acceleration"
    elif gap > 20 and velocity_score > 25:
        signal = "WEAK — some divergence but limited edge"
        stage_hint = "Acceleration"
    elif price_change > volume_change:
        signal = "NEGATIVE — price moved more than volume (late stage)"
        stage_hint = "Saturation or Decay"
    else:
        signal = "NEUTRAL — no clear divergence"
        stage_hint = "Unknown"

    return signal, stage_hint


def run_divergence_check(top_n=5):
    """
    Run full divergence check on top N narratives by velocity.
    """
    scored = score_all_narratives(10)
    top = scored[:top_n]

    results = []

    for n in top:
        print(f"\nAnalyzing: {n['name']} (velocity score: {n['velocity_score']})")
        print(f"  Volume change: {n['volume_change_24h']}% | Price change: {n['avg_change_24h']}%")

        signal, stage_hint = compute_divergence_signal(
            n["name"],
            n["velocity_score"],
            n["volume_change_24h"],
            n["avg_change_24h"]
        )

        print(f"  Signal: {signal}")
        print(f"  Lifecycle hint: {stage_hint}")

        tokens = fetch_category_tokens(n["name"], limit=3)
        if tokens:
            print(f"  Top tokens in this narrative:")
            for t in tokens:
                print(f"    {t['symbol']:<8} price: ${t['price']:<10} 24h: {t['change_24h']}%  7d: {t['change_7d']}%")

        results.append({
            "name": n["name"],
            "velocity_score": n["velocity_score"],
            "volume_change_24h": n["volume_change_24h"],
            "avg_change_24h": n["avg_change_24h"],
            "signal": signal,
            "stage_hint": stage_hint,
            "tokens": tokens,
        })

    return results


if __name__ == "__main__":
    print("Running divergence check on top narratives...\n")
    results = run_divergence_check(top_n=5)

    print("\n" + "=" * 60)
    print("DIVERGENCE SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"\n{r['name']}")
        print(f"  Velocity: {r['velocity_score']} | Stage hint: {r['stage_hint']}")
        print(f"  Signal: {r['signal']}")