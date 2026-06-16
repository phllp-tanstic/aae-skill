import json
import math
import re
import yfinance as yf
from datetime import datetime, timedelta

CRYPTO_SYMBOL_MAP = {
    "FIL": "FIL-USD",
    "AR": "AR-USD",
    "BTT": None,
    "GODS": "GODS-USD",
    "CVX": "CVX-USD",
    "YFI": "YFI-USD",
    "COW": None,
    "ACX": None,
    "RIF": "RIF-USD",
    "IMX": "IMX-USD",
    "MRVLX": None,
    "SAHARA": None,
    "BARD": None,
    "BB": None,
    "TBLLX": None,
    "STRCX": None,
    "INTCX": None,
    "CRCLX": None,
    "AUSD": None,
    "OIK": None,
    "VELVET": None,
    "YB": None,
}


def get_yahoo_symbol(symbol):
    return CRYPTO_SYMBOL_MAP.get(symbol, f"{symbol}-USD")


def fetch_historical_prices(symbol, days=30):
    yahoo_symbol = get_yahoo_symbol(symbol)
    if yahoo_symbol is None:
        return None
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    try:
        import yfinance as yf
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d")
        )
        if df.empty or len(df) < 5:
            return None
        return df[["Close"]].rename(columns={"Close": symbol})
    except Exception:
        return None


def simulate_strategy(prices_df, symbol, spec):
    if prices_df is None or prices_df.empty:
        return None
    prices = prices_df[symbol].dropna().tolist()
    if len(prices) < 5:
        return None

    stage = spec.get("lifecycle_stage", "EMERGENCE")
    stop_loss_raw = spec["strategy"]["stop_loss"]
    stop_loss_match = re.search(r"(\d+)", stop_loss_raw)
    stop_loss_pct = float(stop_loss_match.group(1)) / 100 if stop_loss_match else 0.15

    entry_price = prices[1]
    if entry_price <= 0:
        return None
    position = 1000.0 / entry_price
    portfolio = [1000.0]
    in_position = True
    exit_reason = "time exit"

    for i in range(2, len(prices)):
        current_price = prices[i]
        pnl_pct = (current_price - entry_price) / entry_price

        if in_position:
            if stage == "EMERGENCE" and pnl_pct >= 0.40:
                in_position = False
                exit_reason = "profit target +40%"
            elif stage == "ACCELERATION" and pnl_pct >= 0.25:
                in_position = False
                exit_reason = "profit target +25%"
            elif pnl_pct <= -stop_loss_pct:
                in_position = False
                exit_reason = f"stop loss -{round(stop_loss_pct * 100)}%"

        current_value = position * current_price if in_position else portfolio[-1]
        portfolio.append(current_value)

    return portfolio, exit_reason


def compute_metrics(portfolio_values):
    if not portfolio_values or len(portfolio_values) < 3:
        return None

    initial = portfolio_values[0]
    final = portfolio_values[-1]
    total_return = round((final - initial) / initial * 100, 2)

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
    print(f"\nBacktesting: {spec['narrative']} [{spec['lifecycle_stage']}]")
    print(f"Spec ID: {spec['spec_id']}")
    print(f"Assets : {spec['backtestable_assets']}")

    results = []

    for symbol in spec["backtestable_assets"]:
        print(f"  Fetching {symbol} historical data...")
        prices_df = fetch_historical_prices(symbol, days=days)

        if prices_df is None:
            print(f"  {symbol}: no data available — skipping")
            continue

        result = simulate_strategy(prices_df, symbol, spec)
        if result is None:
            print(f"  {symbol}: insufficient data — skipping")
            continue

        portfolio_values, exit_reason = result
        metrics = compute_metrics(portfolio_values)

        if metrics:
            metrics["symbol"] = symbol
            metrics["exit_reason"] = exit_reason
            results.append(metrics)
            print(f"  {symbol}: return={metrics['total_return_pct']}% | "
                  f"drawdown={metrics['max_drawdown_pct']}% | "
                  f"sharpe={metrics['sharpe_ratio']} | "
                  f"exit={exit_reason}")

    return results


def run_backtest_on_output(json_file="strategy_output.json", days=30):
    with open(json_file, "r") as f:
        data = json.load(f)

    if isinstance(data, list):
        specs = data
    elif isinstance(data, dict) and "strategy_specs" in data:
        specs = data["strategy_specs"]
    else:
        specs = list(data.values())

    print("=" * 65)
    print("AAE BACKTESTER")
    print("=" * 65)
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

    for spec_id, data in all_results.items():
        print(f"\n{data['narrative']} [{data['lifecycle_stage']}]")
        if not data["asset_results"]:
            print("  No backtestable assets with available data")
            continue
        for r in data["asset_results"]:
            verdict = "PASS" if r["total_return_pct"] > 0 and r["sharpe_ratio"] > 0.5 else "REVIEW"
            print(f"  {r['symbol']:<8} "
                  f"return: {r['total_return_pct']:>7}%  "
                  f"drawdown: {r['max_drawdown_pct']:>6}%  "
                  f"sharpe: {r['sharpe_ratio']:>5}  "
                  f"[{verdict}]")

    with open("backtest_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nBacktest results saved to: backtest_results.json")

    return all_results


if __name__ == "__main__":
    run_backtest_on_output("strategy_output.json", days=30)
