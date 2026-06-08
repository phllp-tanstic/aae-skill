import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("CMC_API_KEY")

url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
headers = {"X-CMC_PRO_API_KEY": api_key}

response = requests.get(url, headers=headers)
data = response.json()

print("Status:", response.status_code)
print("BTC Dominance:", round(data["data"]["btc_dominance"], 2), "%")
print("Total Market Cap: $", round(data["data"]["quote"]["USD"]["total_market_cap"] / 1e12, 2), "trillion")
print("CMC API key works!")