import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key = os.getenv("CMC_API_KEY")
headers = {"X-CMC_PRO_API_KEY": api_key}
BASE = "https://pro-api.coinmarketcap.com"

def test_global_metrics():
    url = f"{BASE}/v1/global-metrics/quotes/latest"
    r = requests.get(url, headers=headers)
    data = r.json()["data"]
    print("=== GLOBAL METRICS ===")
    print("Fear & Greed Index:", data.get("fear_greed_value", "N/A"))
    print("BTC Dominance:", round(data["btc_dominance"], 2), "%")
    print("Total Market Cap: $", round(data["quote"]["USD"]["total_market_cap"] / 1e12, 2), "T")
    print()

def test_trending():
    url = f"{BASE}/v1/cryptocurrency/trending/gainers-losers"
    r = requests.get(url, headers=headers, params={"limit": 5})
    data = r.json()
    print("=== TRENDING GAINERS (top 5) ===")
    for coin in data.get("data", {}).get("gainers", [])[:5]:
        name = coin["name"]
        pct = round(coin["quote"]["USD"]["percent_change_24h"], 2)
        print(f"  {name}: +{pct}%")
    print()

def test_latest_listings():
    url = f"{BASE}/v1/cryptocurrency/listings/latest"
    r = requests.get(url, headers=headers, params={"limit": 5, "sort": "percent_change_24h", "sort_dir": "desc"})
    data = r.json()
    print("=== TOP MOVERS (24h) ===")
    for coin in data.get("data", []):
        name = coin["name"]
        symbol = coin["symbol"]
        pct = round(coin["quote"]["USD"]["percent_change_24h"], 2)
        print(f"  {name} ({symbol}): +{pct}%")
    print()

def test_categories():
    url = f"{BASE}/v1/cryptocurrency/categories"
    r = requests.get(url, headers=headers, params={"limit": 5})
    data = r.json()
    print("=== TOP NARRATIVE CATEGORIES ===")
    for cat in data.get("data", [])[:5]:
        name = cat["name"]
        change = round(cat.get("avg_price_change", 0), 2)
        num_tokens = cat.get("num_tokens", "?")
        print(f"  {name}: avg change {change}%, tokens: {num_tokens}")
    print()

test_global_metrics()
test_trending()
test_latest_listings()
test_categories()

print("All CMC tools responding correctly!")