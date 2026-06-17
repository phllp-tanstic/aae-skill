"""
AAE Backtester — CMC OHLCV Edition
=====================================
Uses CoinMarketCap /v1/cryptocurrency/ohlcv/historical for real
narrative token price data. Requires CMC Pro tier or higher.

Replaces yfinance — now backtests actual narrative tokens
instead of Yahoo Finance proxies.
"""

import json
import math
import re
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CMC_API_KEY = os.getenv("CMC_API_KEY")
CMC_HEADERS = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
CMC_BASE = "https://pro-api.coinmarketcap.com"


def fetch_cmc_symbol_id(symbol):
    """
    Resolve a token symbol to its CMC ID.
    Returns the CMC ID integer or None if not found.
    """
    url = f"{CMC_BASE}/v1/cryptocurrency/map"
    params = {"symbol": symbol, "limit": 1}
    try:
        r = requests.get(url, headers=CMC_HEADERS, params=params, timeout=10)
        data = r.json().get("data", [])
        if data:
            return data[0]["id"]
    except Exception:
        pass
    return None


def fetch_historical_prices(symbol, days=30):
    """
    Fetch daily OHLCV for a token using CMC Pro API.
    Returns list of close prices or None if unavailable.
    """
    cmc_id = fetch_cmc_symbol_id(symbol)
    if not cmc_id:
        return None

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    url = f"{CMC_BASE}/v1/cryptocurrency/ohlcv/historical"
    params = {
        "id": cmc_id,
        "time_start": start_date.strftime("%Y-%m-%d"),
        "time_end": end_date.strftime("%Y-%m-%d"),
        "interval": "daily",
        "convert": "USD",
    }

    try:
        r = requests.get(url, headers=CMC_HEADERS, params=params, timeout=15)
        data = r.json()

        if data.get("status", {}).get("error_code", 0) != 0:
            return None

        quotes = data.get("data", {}).get("quotes", [])
        if not quotes or len(quotes) < 5:
            return None

        closes = [q["quote"]["USD"]["close"] for q in quotes if q["quote"]["USD"]["close"]]
        if len(closes) < 5:
            return None

        return closes

    except Exception:
        return None


def simulate_strategy(prices, symbol, spec):
    """
    Simulate strategy execution against daily close prices.
    Entry on day 2 (index 1), monitor from day 3 onward.
    """
    if not prices or len(prices) < 5:
        return None

    stage = spec.get("lifecycle_stage", "EMERGENCE")
    stop_loss_raw = spec["strategy"]["stop_loss"]
    stop_loss_match = re.search(r"(\d+)", stop_loss_raw)
    stop_loss_pct = float(stop_loss_match.group(1)) / 100 if stop_loss_match else 0.15

    profit_targets = {
        "EMERGENCE": 0.40,
        "EARLY_ACCELERATION": 0.25,
        "LATE_ACCELERATION": 0.20,
        "SATURATION": None,
        "DECAY": None,
    }
    profit_target = profit_targets.get(stage, 0.25)

    entry_price = prices[1]
    if entry_price <= 0:
        return None

    position = 1000.0 / entry_price
    portfolio = [1000.0]
    in_position = True
    exit_reason = "time exit"

    for i in range(2, len(prices)):
        current_price = prices[i]
        if current_price <= 0:
            portfolio.append(portfolio[-1])
            continue

        pnl_pct = (current_price - entry_price) / entry_price

        if in_position:
            if profit_target and pnl_pct >= profit_target:
                in_position = False
                exit_reason = f"profit target +{round(profit_target * 100)}%"
            elif pnl_pct <= -stop_loss_pct:
                in_position = False
                exit_reason = f"stop loss -{round(stop_loss_pct * 100)}%"

        current_value = position * current_price if in_position else portfolio[-1]
        portfolio.append(current_value)

    return portfolio, exit_reason


def compute_metrics(portfolio_values):
    """Compute return, drawdown, and Sharpe ratio from portfolio curve."""
    if not portfolio_values or len(portfolio_values) < 3:
        return None

    initial = portfolio_values[0]
    final = portfolio_values[-1]
    total_return = round((final - initial) / initial * 100, 2)

    if total_return == 0.0 and all(v == initial for v in portfolio_values):
        return None

    peak = portfolio_values[0]
    max_dd = 0
    for v in portfolio_values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        if dd > max_dd:
            max_dd = dd
    max_drawdown = round(max_dd * 100, 2)

    daily_returns = []
    for i in range(1, len(portfolio_values)):
        prev = portfolio_values[i - 1]
        if prev > 0:
            daily_returns.append((portfolio_values[i] - prev) / prev)

    if len(daily_returns) > 1:
        avg = sum(daily_returns) / len(daily_returns)
        variance = sum((r - avg) ** 2 for r in daily_returns) / len(daily_returns)
        std = math.sqrt(variance)
        sharpe = round((avg / std * math.sqrt(365)) if std > 0 else 0, 2)
    else:
        sharpe = 0

    return {
        "total_return_pct": total_return,
        "max_drawdown_pct": max_drawdown,
        "sharpe_ratio": sharpe,
        "initial_value": round(initial, 2),
        "final_value": round(final, 2),
        "days_simulated": len(portfolio_values),
    }


def backtest_spec(spec, days=30):
    """Backtest a single strategy spec against all its assets."""
    print(f"\nBacktesting: {spec['narrative']} [{spec['lifecycle_stage']}]")
    print(f"Spec ID: {spec['spec_id']}")
    print(f"Assets : {spec['backtestable_assets']}")

    if spec.get("lifecycle_stage") == "DECAY":
        print(f"  SKIP — DECAY spec has no entry signal")
        return []

    results = []

    for symbol in spec["backtestable_assets"]:
        print(f"  Fetching {symbol} via CMC OHLCV...")
        prices = fetch_historical_prices(symbol, days=days)

        if prices is None:
            print(f"  {symbol}: no CMC data — skipping")
            continue

        result = simulate_strategy(prices, symbol, spec)
        if result is None:
            print(f"  {symbol}: insufficient price data — skipping")
            continue

        portfolio_values, exit_reason = result
        metrics = compute_metrics(portfolio_values)

        if metrics:
            metrics["symbol"] = symbol
            metrics["exit_reason"] = exit_reason
            results.append(metrics)
            verdict = "PASS" if metrics["total_return_pct"] > 0 and metrics["sharpe_ratio"] > 0.5 else "REVIEW"
            print(f"  {symbol}: return={metrics['total_return_pct']}% | "
                  f"drawdown={metrics['max_drawdown_pct']}% | "
                  f"sharpe={metrics['sharpe_ratio']} | "
                  f"exit={exit_reason} | [{verdict}]")
        else:
            print(f"  {symbol}: flat data — skipping")

    return results


def run_backtest_on_output(json_file="strategy_output.json", days=30):
    """Run backtest on all specs in output file."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        specs = data
    elif isinstance(data, dict) and "strategy_specs" in data:
        specs = data["strategy_specs"]
    else:
        specs = list(data.values())

    print("=" * 65)
    print("AAE BACKTESTER — CMC OHLCV Edition")
    print("=" * 65)
    print(f"Data source       : CoinMarketCap Pro OHLCV")
    print(f"Loading specs from: {json_file}")
    print(f"Backtest window   : {days} days")
    print(f"Specs to test     : {len(specs)}")

    all_results = {}

    for spec in specs:
        results = backtest_spec(spec, days=days)
        all_results[spec["spec_id"]] = {
            "narrative": spec["narrative"],
            "lifecycle_stage": spec["lifecycle_stage"],
            "opportunity_score": spec["opportunity_score"],
            "asset_results": results,
        }

    print("\n" + "=" * 65)
    print("BACKTEST SUMMARY")
    print("=" * 65)

    total_assets = 0
    passing = 0

    for spec_id, data in all_results.items():
        print(f"\n{data['narrative']} [{data['lifecycle_stage']}]")
        if not data["asset_results"]:
            print("  No backtestable assets with available data")
            continue
        for r in data["asset_results"]:
            total_assets += 1
            verdict = "PASS" if r["total_return_pct"] > 0 and r["sharpe_ratio"] > 0.5 else "REVIEW"
            if verdict == "PASS":
                passing += 1
            print(f"  {r['symbol']:<8} "
                  f"return: {r['total_return_pct']:>7}%  "
                  f"drawdown: {r['max_drawdown_pct']:>6}%  "
                  f"sharpe: {r['sharpe_ratio']:>5}  "
                  f"exit: {r['exit_reason']:<25} [{verdict}]")

    if total_assets > 0:
        print(f"\n  Assets tested : {total_assets}")
        print(f"  Passing       : {passing}")
        print(f"  Pass rate     : {round(passing/total_assets*100)}%")

    with open("backtest_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print("\nBacktest results saved to: backtest_results.json")

    return all_results


if __name__ == "__main__":
    run_backtest_on_output("strategy_output.json", days=30)