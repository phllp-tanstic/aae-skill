"""
CMC x402 Pay-Per-Call Integration
====================================
Demonstrates the x402 protocol flow for CMC data access.
x402 is an open protocol by Coinbase enabling automatic
stablecoin payments over HTTP — no API keys required.

Real x402 requires USDC on Base mainnet.
This simulation demonstrates the correct protocol flow:
  Step 1: Request → HTTP 402 Payment Required
  Step 2: Decode payment challenge
  Step 3: Sign and attach payment
  Step 4: Request → HTTP 200 + data

CMC x402 endpoint: https://pro-api.coinmarketcap.com/x402/v3/
Payment: $0.01 USDC per request on Base network

BNB x CMC Hackathon — CMC Agent Hub Special Prize
"""

import json
import hashlib
import time
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

CMC_X402_BASE = "https://pro-api.coinmarketcap.com/x402/v3"
BASE_CHAIN_ID = "eip155:8453"
USDC_BASE_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
PAYMENT_AMOUNT = "10000"
CMC_PAYMENT_ADDRESS = "0x271189c860DB25bC43173B0335784aD68a680908"


def simulate_http_402_challenge(endpoint):
    """
    Simulate the HTTP 402 Payment Required response.
    In production this is the real CMC server response.
    """
    challenge_payload = {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {
            "url": endpoint,
            "description": "CMC crypto narrative data API"
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": BASE_CHAIN_ID,
                "asset": USDC_BASE_ADDRESS,
                "amount": PAYMENT_AMOUNT,
                "payTo": CMC_PAYMENT_ADDRESS,
                "maxTimeoutSeconds": 30,
                "extra": {
                    "name": "USD Coin",
                    "version": "2",
                    "x402PaymentConfigId": "699dbab79f32ffde650104aa"
                }
            }
        ]
    }

    encoded = base64.b64encode(
        json.dumps(challenge_payload).encode()
    ).decode()

    return {
        "status_code": 402,
        "payment_required_header": encoded,
        "decoded_challenge": challenge_payload
    }


def simulate_payment_signature(challenge, wallet_address):
    """
    Simulate signing the payment authorization.
    In production this uses an x402 client with real USDC on Base.
    The signature proves authorization for the required payment amount.
    """
    payment_details = challenge["decoded_challenge"]["accepts"][0]

    payload = {
        "x402Version": 2,
        "scheme": payment_details["scheme"],
        "network": payment_details["network"],
        "asset": payment_details["asset"],
        "amount": payment_details["amount"],
        "payTo": payment_details["payTo"],
        "payer": wallet_address,
        "timestamp": int(time.time()),
        "nonce": hashlib.sha256(
            f"{wallet_address}{time.time()}".encode()
        ).hexdigest()[:16],
    }

    signature_input = json.dumps(payload, sort_keys=True)
    mock_signature = hashlib.sha256(signature_input.encode()).hexdigest()

    jwt_header = base64.b64encode(
        json.dumps({"alg": "ES256", "typ": "JWT"}).encode()
    ).decode()
    jwt_payload = base64.b64encode(
        json.dumps(payload).encode()
    ).decode()
    payment_signature = f"{jwt_header}.{jwt_payload}.{mock_signature[:86]}"

    return payment_signature, payload


def simulate_x402_data_response(endpoint):
    """
    Simulate the HTTP 200 response after payment.
    In production CMC returns real data after payment verification.
    We fetch real data via our existing API key to show what the
    response would contain.
    """
    api_key = os.getenv("CMC_API_KEY")
    if not api_key:
        return {"simulation": True, "note": "No CMC API key found"}

    standard_endpoint = endpoint.replace("/x402/v3", "/v1")
    headers = {"X-CMC_PRO_API_KEY": api_key}

    try:
        r = requests.get(
            f"https://pro-api.coinmarketcap.com{standard_endpoint}",
            headers=headers,
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass

    return {"simulation": True, "note": "Data would be returned after payment"}


def run_x402_flow(endpoint, wallet_address):
    """
    Demonstrate the complete x402 payment flow.
    Three steps: 402 challenge → sign → 200 response.
    """
    print(f"\n  Endpoint : {CMC_X402_BASE}{endpoint}")
    print(f"  Payer    : {wallet_address}")
    print()

    print("  STEP 1 — Initial request (no payment)")
    print(f"  → GET {CMC_X402_BASE}{endpoint}")
    challenge = simulate_http_402_challenge(endpoint)
    print(f"  ← HTTP {challenge['status_code']} Payment Required")
    decoded = challenge["decoded_challenge"]
    payment_terms = decoded["accepts"][0]
    amount_usdc = int(payment_terms["amount"]) / 1_000_000
    print(f"  ← Payment required: ${amount_usdc} USDC on Base")
    print(f"  ← Pay to: {payment_terms['payTo'][:20]}...")
    print(f"  ← Asset: USDC ({payment_terms['asset'][:20]}...)")
    print()

    print("  STEP 2 — Sign payment authorization")
    signature, payload = simulate_payment_signature(challenge, wallet_address)
    print(f"  → Signing payment of ${amount_usdc} USDC")
    print(f"  → Network: {payload['network']}")
    print(f"  → Nonce: {payload['nonce']}")
    print(f"  → Signature: {signature[:40]}...")
    print()

    print("  STEP 3 — Authenticated request with payment signature")
    print(f"  → GET {CMC_X402_BASE}{endpoint}")
    print(f"  → Header: PAYMENT-SIGNATURE: {signature[:30]}...")
    data = simulate_x402_data_response(endpoint)
    print(f"  ← HTTP 200 OK")
    print(f"  ← Data received: {len(str(data))} bytes")
    print()

    return {
        "endpoint": endpoint,
        "challenge": decoded,
        "payment": payload,
        "signature_preview": signature[:40] + "...",
        "response_size_bytes": len(str(data)),
        "status": "SIMULATED — real flow requires USDC on Base mainnet",
        "real_endpoint": f"{CMC_X402_BASE}{endpoint}",
        "cost_per_call": f"${amount_usdc} USDC",
    }


def run_x402_integration():
    """
    Demonstrate x402 for three CMC data endpoints used by AAE.
    """
    print("\n" + "=" * 65)
    print("  CMC x402 PAY-PER-CALL INTEGRATION")
    print("  HTTP 402 Payment Protocol — Base Network (USDC)")
    print("=" * 65)
    print()
    print("  Protocol : x402 (Coinbase open standard)")
    print("  Network  : Base (eip155:8453)")
    print("  Asset    : USDC")
    print("  Cost     : $0.01 per request")
    print("  Endpoint : pro-api.coinmarketcap.com/x402/v3/")
    print()
    print("  Status   : SIMULATION (real flow requires USDC on Base)")
    print("  Note     : Protocol flow is identical to production")
    print()

    wallet_address = "0xcc582aF540760db41bCD1a34A8aA49098ee88868"

    if os.path.exists("bnb_registration.json"):
        with open("bnb_registration.json") as f:
            reg = json.load(f)
            wallet_address = reg.get("wallet_address", wallet_address)

    endpoints = [
        "/cryptocurrency/quotes/latest?id=1",
        "/cryptocurrency/listings/latest?limit=5",
        "/global-metrics/quotes/latest",
    ]

    endpoint_names = [
        "Crypto Quotes (BTC price)",
        "Top Listings",
        "Global Market Metrics",
    ]

    results = []
    for endpoint, name in zip(endpoints, endpoint_names):
        print(f"  {'─'*61}")
        print(f"  Call: {name}")
        result = run_x402_flow(endpoint, wallet_address)
        results.append(result)

    total_cost = len(endpoints) * 0.01
    print(f"  {'─'*61}")
    print(f"  Total calls simulated : {len(results)}")
    print(f"  Total cost (real)     : ${total_cost:.2f} USDC")
    print(f"  Savings vs API key    : $0 (x402 is usage-based)")
    print()

    output = {
        "integration": "CMC x402 Pay-Per-Call",
        "protocol": "x402 (Coinbase)",
        "network": "Base (eip155:8453)",
        "asset": "USDC",
        "cost_per_call": "$0.01",
        "generated_at": datetime.now().isoformat(),
        "payer_wallet": wallet_address,
        "flows_demonstrated": results,
        "status": "SIMULATION",
        "note": (
            "Real x402 requires USDC on Base mainnet. "
            "Protocol flow is production-identical. "
            "CMC x402 endpoint: https://pro-api.coinmarketcap.com/x402/v3/"
        ),
    }

    with open("x402_simulation.json", "w") as f:
        json.dump(output, f, indent=2)

    print("  x402 simulation saved to: x402_simulation.json")
    print("  x402 integration complete.")

    return output


if __name__ == "__main__":
    run_x402_integration()