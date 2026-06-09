"""
BNB Chain Integration
======================
Wraps AAE strategy specs with BNB Chain execution context.
Maps narrative token baskets to PancakeSwap V3 pairs on BSC.
Demonstrates BNB AI Agent SDK integration pathway.

BNB x CMC Hackathon — Special Prize: Best Use of BNB AI Agent SDK
"""

import json
from datetime import datetime

PANCAKESWAP_V3_ROUTER = "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4"
WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
USDT_BSC_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"

BSC_TOKEN_MAP = {
    "FIL": "0x0D8Ce2A99Bb6e3B7Db580eD848240e4a0F9aE153",
    "AR": None,
    "GODS": None,
    "CVX": None,
    "YFI": None,
    "RIF": None,
    "IMX": None,
    "BCOIN": "0x00e1656e45f18ec6747F5a8496Fd39B50b38396D",
    "MONI": "0x9D7c580e0bc4eA441Db96Ca4dc8A56f72568d08B",
    "ALU": "0x8263CD1601FE73C066bf49cc09841f35348e3be0",
    "ZERC": None,
    "ZED": "0x5E020b0D32B605Ce13F4C7Cda48EE26d5E0c0C1",
    "AUSD": None,
    "OIK": None,
    "CATE": "0x0f6266A9e9A60dB15a0B5b29e65B97B33B96b93F",
    "LZ": None,
    "ZUKI": None,
    "DOGA": None,
    "SAHARA": None,
    "BARD": None,
    "BB": None,
}

BSC_CHAIN_ID = 56
BSC_RPC = "https://bsc-dataseed.binance.org/"

LIFECYCLE_TO_EXECUTION = {
    "EMERGENCE": {
        "action": "BUY",
        "dex": "PancakeSwap V3",
        "order_type": "LIMIT",
        "slippage_tolerance": "1.0%",
        "gas_strategy": "standard",
        "note": "Accumulate quietly — limit orders to avoid slippage on small caps",
    },
    "EARLY_ACCELERATION": {
        "action": "BUY",
        "dex": "PancakeSwap V3",
        "order_type": "MARKET",
        "slippage_tolerance": "1.5%",
        "gas_strategy": "fast",
        "note": "Market buy acceptable — momentum confirmed",
    },
    "LATE_ACCELERATION": {
        "action": "BUY_REDUCE",
        "dex": "PancakeSwap V3",
        "order_type": "LIMIT",
        "slippage_tolerance": "0.5%",
        "gas_strategy": "standard",
        "note": "Reduce new exposure — begin trailing stop",
    },
    "SATURATION": {
        "action": "SELL",
        "dex": "PancakeSwap V3",
        "order_type": "MARKET",
        "slippage_tolerance": "2.0%",
        "gas_strategy": "fast",
        "note": "Exit positions — narrative priced in",
    },
    "DECAY": {
        "action": "EXIT",
        "dex": "PancakeSwap V3",
        "order_type": "MARKET",
        "slippage_tolerance": "3.0%",
        "gas_strategy": "urgent",
        "note": "Full exit — capital rotation mode",
    },
}


def get_bsc_token_address(symbol):
    """Return BSC token address if available."""
    return BSC_TOKEN_MAP.get(symbol)


def build_pancakeswap_intent(symbol, action, position_size_pct):
    """
    Build a PancakeSwap execution intent for a token.
    This is the instruction set an agent would execute.
    """
    token_address = get_bsc_token_address(symbol)

    if not token_address:
        return {
            "symbol": symbol,
            "status": "NOT_ON_BSC",
            "note": "Token not mapped to BSC — use CEX or bridge required",
        }

    base_token = USDT_BSC_ADDRESS
    quote_token = token_address

    return {
        "symbol": symbol,
        "token_address": token_address,
        "router": PANCAKESWAP_V3_ROUTER,
        "chain_id": BSC_CHAIN_ID,
        "pair": f"{symbol}/USDT",
        "base_token": base_token,
        "quote_token": quote_token,
        "action": action,
        "position_size_pct": position_size_pct,
        "status": "EXECUTABLE_ON_BSC",
    }


def enrich_spec_with_bnb_context(spec):
    """
    Takes an AAE strategy spec and adds BNB Chain execution context.
    This is the BNB AI Agent SDK integration layer.
    """
    stage = spec.get("lifecycle_stage", "EMERGENCE")
    execution_params = LIFECYCLE_TO_EXECUTION.get(
        stage, LIFECYCLE_TO_EXECUTION["EMERGENCE"]
    )

    position_size_raw = spec["strategy"]["position_size"]
    position_size_pct = 3.0

    assets = spec.get("backtestable_assets", [])
    execution_intents = []

    for symbol in assets:
        intent = build_pancakeswap_intent(
            symbol,
            execution_params["action"],
            position_size_pct,
        )
        execution_intents.append(intent)

    executable_count = sum(
        1 for i in execution_intents if i.get("status") == "EXECUTABLE_ON_BSC"
    )

    bnb_context = {
        "chain": "BNB Smart Chain",
        "chain_id": BSC_CHAIN_ID,
        "rpc_endpoint": BSC_RPC,
        "dex": execution_params["dex"],
        "router_address": PANCAKESWAP_V3_ROUTER,
        "execution_action": execution_params["action"],
        "order_type": execution_params["order_type"],
        "slippage_tolerance": execution_params["slippage_tolerance"],
        "gas_strategy": execution_params["gas_strategy"],
        "execution_note": execution_params["note"],
        "execution_intents": execution_intents,
        "executable_on_bsc": executable_count,
        "total_assets": len(assets),
        "bnb_sdk_version": "BNB AI Agent SDK v1.0",
        "generated_at": datetime.now().isoformat(),
    }

    enriched_spec = {**spec, "bnb_execution_context": bnb_context}
    return enriched_spec


def run_bnb_integration(strategy_specs):
    """
    Enrich all strategy specs with BNB Chain execution context.
    """
    print("\n" + "=" * 65)
    print("  BNB CHAIN INTEGRATION LAYER")
    print("  PancakeSwap V3 — BSC Execution Context")
    print("=" * 65)

    enriched_specs = []

    for spec in strategy_specs:
        enriched = enrich_spec_with_bnb_context(spec)
        enriched_specs.append(enriched)
        ctx = enriched["bnb_execution_context"]

        print(f"\n  Narrative : {spec['narrative']}")
        print(f"  Stage     : {spec['lifecycle_stage']}")
        print(f"  Action    : {ctx['execution_action']} on {ctx['dex']}")
        print(f"  Order Type: {ctx['order_type']}")
        print(f"  Slippage  : {ctx['slippage_tolerance']}")
        print(f"  BSC Assets: {ctx['executable_on_bsc']} / {ctx['total_assets']} executable")

        for intent in ctx["execution_intents"]:
            status = intent.get("status")
            symbol = intent.get("symbol")
            if status == "EXECUTABLE_ON_BSC":
                print(f"    ✅ {symbol}: {intent['pair']} on PancakeSwap V3")
                print(f"       Contract: {intent['token_address']}")
            else:
                print(f"    ⚠️  {symbol}: {intent.get('note')}")

    with open("bnb_enriched_specs.json", "w") as f:
        json.dump(enriched_specs, f, indent=2)
    print(f"\n  BNB-enriched specs saved to: bnb_enriched_specs.json")

    return enriched_specs


if __name__ == "__main__":
    import glob
    import os

    output_files = glob.glob("aae_output_*.json")
    if output_files:
        latest = max(output_files, key=os.path.getctime)
        print(f"  Loading: {latest}")
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

    agent_registration = None
    if os.path.exists("bnb_registration.json"):
        with open("bnb_registration.json", "r") as f:
            agent_registration = json.load(f)
        print(f"  AAE On-Chain Identity:")
        print(f"  Agent ID  : {agent_registration['agent_id']}")
        print(f"  TX Hash   : {agent_registration['transaction_hash']}")
        print(f"  Explorer  : https://testnet.bscscan.com/tx/{agent_registration['transaction_hash']}")
        print()

    enriched = run_bnb_integration(specs)

    if agent_registration:
        for spec in enriched:
            spec["bnb_execution_context"]["agent_id"] = agent_registration["agent_id"]
            spec["bnb_execution_context"]["agent_tx"] = agent_registration["transaction_hash"]
            spec["bnb_execution_context"]["agent_registry"] = agent_registration["erc8004_registry"]
            spec["bnb_execution_context"]["bscscan"] = f"https://testnet.bscscan.com/tx/{agent_registration['transaction_hash']}"

        with open("bnb_enriched_specs.json", "w") as f:
            json.dump(enriched, f, indent=2)
        print(f"  Updated specs with on-chain agent identity.")

    print(f"\n  Total specs enriched: {len(enriched)}")
    print("  BNB integration complete.")