"""
Trust Wallet Agent Kit Integration
====================================
Uses the real TWAK CLI (v0.18.0) for:
1. Live token price feeds across chains
2. Trending token cross-validation (including BNB-native)
3. Real wallet signing of strategy specs via self-custody key
4. x402 quote against CMC endpoint

All signing uses twak wallet sign-message — keys never leave the machine.

BNB x CMC Hackathon — Special Prize: Best Use of Trust Wallet Agent Kit
"""

import subprocess
import json
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TWAK_CMD = r"C:\Users\Aseja Oluwatobi\AppData\Roaming\npm\twak.cmd"


def run_twak(args, timeout=30):
    """Run a twak CLI command and return raw output."""
    try:
        result = subprocess.run(
            [TWAK_CMD] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        output = result.stdout.strip()
        error = result.stderr.strip() if result.returncode != 0 else None
        return output, error
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception as e:
        return None, str(e)


def get_token_price(symbol):
    """Get live token price via TWAK."""
    output, error = run_twak(["price", symbol])
    if error or not output:
        return None
    lines = output.strip().split("\n")
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            price_str = parts[1].replace("$", "").replace(",", "")
            try:
                return {
                    "symbol": parts[0],
                    "price_usd": float(price_str),
                    "chain": parts[2] if len(parts) > 2 else "unknown",
                    "source": "Trust Wallet Agent Kit",
                }
            except ValueError:
                continue
    return None


def get_trending_tokens(category=None):
    """Get trending tokens via TWAK, optionally filtered by category."""
    args = ["trending", "--json"]
    if category:
        args += ["--category", category]
    output, error = run_twak(args)
    if error or not output:
        args_plain = ["trending"]
        if category:
            args_plain += ["--category", category]
        output, error = run_twak(args_plain)
    if not output:
        return []
    try:
        data = json.loads(output)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("tokens", data.get("data", []))
    except json.JSONDecodeError:
        pass
    trending = []
    for line in output.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 2:
            symbol = parts[0]
            price_part = next((p for p in parts if p.startswith("$")), None)
            change_part = next((p for p in parts if "%" in p), None)
            if price_part:
                trending.append({
                    "symbol": symbol,
                    "price": price_part,
                    "change_24h": change_part or "N/A",
                })
    return trending


def sign_strategy_spec(spec):
    """
    Sign a strategy spec using real TWAK self-custody wallet signing.
    Uses twak wallet sign-message --chain bsc which signs with the
    actual BSC private key — keys never leave the machine.
    """
    signable = {
        "spec_id": spec.get("spec_id"),
        "narrative": spec.get("narrative"),
        "lifecycle_stage": spec.get("lifecycle_stage"),
        "opportunity_score": spec.get("opportunity_score"),
        "entry_rule": spec.get("strategy", {}).get("entry_rule"),
        "stop_loss": spec.get("strategy", {}).get("stop_loss"),
        "time_horizon": spec.get("strategy", {}).get("time_horizon"),
        "backtestable_assets": spec.get("backtestable_assets"),
        "generated_at": spec.get("generated_at"),
    }
    canonical = json.dumps(signable, sort_keys=True, separators=(",", ":"))
    spec_hash = hashlib.sha256(canonical.encode()).hexdigest()
    message = f"AAE:{spec_hash[:32]}"
    output, error = run_twak([
        "wallet", "sign-message",
        "--chain", "bsc",
        "--message", message,
        "--json"
    ])
    if error or not output:
        return None, error
    try:
        result = json.loads(output)
        return {
            "spec_id": spec.get("spec_id"),
            "narrative": spec.get("narrative"),
            "lifecycle_stage": spec.get("lifecycle_stage"),
            "spec_hash": spec_hash,
            "message_signed": message,
            "signature": result.get("signature"),
            "signed_by": result.get("address"),
            "chain": result.get("chain"),
            "method": "twak wallet sign-message (ECDSA secp256k1)",
            "custody": "self-custody — key never left local machine",
            "signed_at": datetime.now().isoformat(),
        }, None
    except json.JSONDecodeError:
        return None, f"parse error: {output[:100]}"


def x402_quote_via_twak(url):
    """
    Get x402 payment quote using TWAK's native x402 support.
    Falls back to CMC x402 endpoint if primary fails.
    """
    output, error = run_twak(["x402", "quote", url], timeout=20)
    if output and "402" not in str(error or ""):
        return output, None

    fallback_url = "https://mcp.coinmarketcap.com/x402/mcp"
    output2, error2 = run_twak(["x402", "quote", fallback_url], timeout=20)
    if output2:
        return output2, None

    return None, f"Primary: {error} | Fallback: {error2}"


def run_trust_wallet_integration(specs):
    """Full Trust Wallet Agent Kit integration."""
    print("\n" + "=" * 65)
    print("  TRUST WALLET AGENT KIT INTEGRATION")
    print(f"  twak v0.18.0 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    results = {}
    twak_prices = {}
    all_signed = []

    print("\n  ── Live Price Feed ────────────────────────────────────")
    for symbol in ["BNB", "ETH", "BTC"]:
        price_data = get_token_price(symbol)
        if price_data:
            twak_prices[symbol] = price_data
            print(f"  ✅ {price_data['symbol']:<6} ${price_data['price_usd']:<12} [{price_data['chain']}]")
            results[f"price_{symbol}"] = "SUCCESS"
        else:
            print(f"  ⚠️  {symbol}: unavailable")
            results[f"price_{symbol}"] = "FAILED"

    print("\n  ── Trending — Global ──────────────────────────────────")
    trending_global = get_trending_tokens()
    if trending_global:
        print(f"  ✅ {len(trending_global)} trending tokens retrieved")
        for t in trending_global[:5]:
            sym = t.get("symbol", t.get("name", "?"))
            price = t.get("price", t.get("priceUsd", "?"))
            change = t.get("change_24h", t.get("priceChange24h", "?"))
            print(f"     {sym:<10} {str(price):<12} {change}")
        results["trending_global"] = "SUCCESS"
    else:
        print("  ⚠️  No trending data")
        results["trending_global"] = "FAILED"

    print("\n  ── Trending — BNB Chain ───────────────────────────────")
    trending_bnb = get_trending_tokens(category="bnb")
    if trending_bnb:
        print(f"  ✅ {len(trending_bnb)} BNB-native trending tokens")
        for t in trending_bnb[:5]:
            sym = t.get("symbol", t.get("name", "?"))
            price = t.get("price", t.get("priceUsd", "?"))
            change = t.get("change_24h", t.get("priceChange24h", "?"))
            print(f"     {sym:<10} {str(price):<12} {change}")
        results["trending_bnb"] = "SUCCESS"
    else:
        print("  ⚠️  No BNB trending data")
        results["trending_bnb"] = "FAILED"

    print("\n  ── Self-Custody Strategy Spec Signing ────────────────")
    print("  Method: twak wallet sign-message --chain bsc")
    print("  Keys never leave the local machine (ECDSA secp256k1)")
    print()
    for spec in specs[:3]:
        print(f"  Signing: {spec.get('narrative')} [{spec.get('lifecycle_stage')}]")
        signed, error = sign_strategy_spec(spec)
        if signed:
            all_signed.append(signed)
            print(f"  ✅ Signed by  : {signed['signed_by']}")
            print(f"     Spec hash  : {signed['spec_hash'][:32]}...")
            print(f"     Signature  : {signed['signature'][:32]}...")
            print(f"     Custody    : {signed['custody']}")
            results[f"sign_{spec.get('spec_id', 'spec')}"] = "SUCCESS"
        else:
            print(f"  ⚠️  {error}")
            results[f"sign_{spec.get('spec_id', 'spec')}"] = f"FAILED: {error}"
        print()

    print("\n  ── x402 Quote via TWAK ────────────────────────────────")
    x402_url = "https://pro-api.coinmarketcap.com/x402/v3/global-metrics/quotes/latest"
    print(f"  twak x402 quote {x402_url}")
    quote_output, quote_error = x402_quote_via_twak(x402_url)
    if quote_output:
        print(f"  ✅ x402 quote received:")
        for line in quote_output.split("\n")[:6]:
            if line.strip():
                print(f"     {line.strip()}")
        results["x402_quote"] = "SUCCESS"
    else:
        print(f"  ⚠️  {quote_error}")
        results["x402_quote"] = f"FAILED: {quote_error}"

    successful = sum(1 for v in results.values() if v == "SUCCESS")
    total = len(results)

    output = {
        "integration": "Trust Wallet Agent Kit",
        "twak_version": "0.18.0",
        "generated_at": datetime.now().isoformat(),
        "capabilities_used": [
            "price — live token prices",
            "trending — global and BNB-native",
            "wallet sign-message — self-custody spec signing",
            "x402 quote — payment preview",
        ],
        "live_prices": twak_prices,
        "trending_global": trending_global[:10] if trending_global else [],
        "trending_bnb": trending_bnb[:10] if trending_bnb else [],
        "signed_strategy_specs": all_signed,
        "results": results,
        "successful_calls": successful,
        "total_calls": total,
    }

    with open("twak_intelligence.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n  {'─'*61}")
    print(f"  TWAK calls successful : {successful} / {total}")
    print(f"  Signed specs          : {len(all_signed)}")
    print(f"  Output saved          : twak_intelligence.json")
    print("  Trust Wallet integration complete.")

    return output


if __name__ == "__main__":
    import glob

    output_files = glob.glob("aae_output_*.json")
    if output_files:
        latest = max(output_files, key=os.path.getctime)
        with open(latest, "r") as f:
            data = json.load(f)
    else:
        with open("strategy_output.json", "r") as f:
            data = json.load(f)

    if isinstance(data, list):
        specs = data
    elif isinstance(data, dict) and "strategy_specs" in data:
        specs = data["strategy_specs"]
    else:
        specs = list(data.values())

    run_trust_wallet_integration(specs)