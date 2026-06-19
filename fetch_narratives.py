import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("CMC_API_KEY")
headers = {"X-CMC_PRO_API_KEY": api_key}
BASE = "https://pro-api.coinmarketcap.com"

def fetch_narratives(limit=10):
    """
    Fetches top narrative categories from CMC.
    Returns a list of narratives with name, token count,
    average price change, and market cap change.
    """
    url = f"{BASE}/v1/cryptocurrency/categories"
    params = {"limit": 50}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ERROR: CMC API call failed — {e}")
        return []
    narratives = []

    narratives = []

    for cat in data.get("data", []):
        name = cat.get("name", "")
        num_tokens = cat.get("num_tokens", 0)
        avg_change_24h = round(cat.get("avg_price_change", 0), 4)
        market_cap = cat.get("market_cap", 0)
        market_cap_change = round(cat.get("market_cap_change", 0), 4)
        volume = cat.get("volume", 0)
        volume_change = round(cat.get("volume_change", 0), 4)

        if num_tokens < 3:
            continue

        narratives.append({
            "name": name,
            "num_tokens": num_tokens,
            "avg_change_24h": avg_change_24h,
            "market_cap": market_cap,
            "market_cap_change_24h": market_cap_change,
            "volume": volume,
            "volume_change_24h": volume_change,
        })

    narratives.sort(key=lambda x: x["volume_change_24h"], reverse=True)

    return narratives[:limit]


if __name__ == "__main__":
    print("Fetching top narratives from CMC...\n")
    narratives = fetch_narratives(10)

    for i, n in enumerate(narratives, 1):
        print(f"{i}. {n['name']}")
        print(f"   Tokens: {n['num_tokens']}")
        print(f"   Avg price change 24h: {n['avg_change_24h']}%")
        print(f"   Volume change 24h: {n['volume_change_24h']}%")
        print(f"   Market cap change 24h: {n['market_cap_change_24h']}%")
        print()

    print(f"Total narratives fetched: {len(narratives)}")