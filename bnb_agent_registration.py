"""
BNB AI Agent SDK Integration
==============================
Registers the Attention Arbitrage Engine as an on-chain AI agent
using ERC-8004 identity standard on BSC Testnet.

Gas is free on testnet via MegaFuel paymaster sponsorship.
No real money required.

BNB x CMC Hackathon — Special Prize: Best Use of BNB AI Agent SDK
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


def setup_wallet():
    """
    Generate or load the AAE agent wallet.
    On first run: generates a new wallet and saves encrypted keystore.
    On subsequent runs: loads from keystore using password only.
    """
    from bnbagent import ERC8004Agent, EVMWalletProvider

    password = os.getenv("BNB_WALLET_PASSWORD", "aae-hackathon-2026")
    private_key = os.getenv("BNB_PRIVATE_KEY", None)

    print("Setting up AAE agent wallet...")

    wallet = EVMWalletProvider(
        password=password,
        private_key=private_key,
    )

    print(f"  Wallet address: {wallet.address}")
    print(f"  Network: BSC Testnet (Chain ID: 97)")
    print()

    return wallet


def register_aae_agent(wallet):
    """
    Register the Attention Arbitrage Engine as an on-chain agent
    using ERC-8004 identity standard.
    Gas is sponsored by MegaFuel paymaster on testnet.
    """
    from bnbagent import ERC8004Agent, AgentEndpoint

    print("Initializing ERC-8004 agent registry...")
    sdk = ERC8004Agent(network="bsc-testnet", wallet_provider=wallet)

    agent_uri = sdk.generate_agent_uri(
        name="attention-arbitrage-engine",
        description=(
            "An AI-powered narrative intelligence system that detects "
            "attention-price divergence, classifies lifecycle stage, "
            "predicts narrative half-life, and generates backtestable "
            "crypto trading strategies before market consensus forms."
        ),
        endpoints=[
            AgentEndpoint(
                name="AAE-Skill",
                endpoint="https://github.com/phllp-tanstic/aae-skill",
                version="2.0.0",
            ),
        ],
    )

    print("Registering AAE on BNB Chain (BSC Testnet)...")
    print("  Gas: sponsored by MegaFuel paymaster (free)")
    print()

    result = sdk.register_agent(agent_uri=agent_uri)

    print("AAE Agent registered on-chain!")
    print(f"  Agent ID  : {result['agentId']}")
    print(f"  TX Hash   : {result['transactionHash']}")
    print(f"  Block     : {result.get('blockNumber', 'pending')}")
    print()

    return result, sdk


def verify_registration(sdk, agent_id):
    """Verify the agent is discoverable on-chain."""
    print(f"Verifying on-chain registration for Agent ID: {agent_id}...")

    agent_info = sdk.get_agent_info(agent_id=agent_id)
    print(f"  Name     : {agent_info.get('name', 'N/A')}")
    print(f"  Agent ID : {agent_info.get('token_id', 'N/A')}")
    print(f"  Owner    : {agent_info.get('owner', 'N/A')}")
    print()

    print("Querying full agent registry...")
    all_agents = sdk.get_all_agents()
    items = all_agents.get("items", [])
    print(f"  Total registered agents: {len(items)}")
    for agent in items[:5]:
        print(f"  Agent #{agent.get('token_id')}: {agent.get('name', 'unnamed')} — {agent.get('owner', '')[:20]}...")
    print()

    return agent_info


def save_registration(wallet_address, result, agent_info):
    """Save registration details for use in demo."""
    registration = {
        "engine": "Attention Arbitrage Engine v2.0",
        "network": "BSC Testnet",
        "chain_id": 97,
        "wallet_address": wallet_address,
        "agent_id": result["agentId"],
        "transaction_hash": result["transactionHash"],
        "erc8004_registry": "0x8004A818BFB912233c491871b3d84c89A494BD9e",
        "agent_info": agent_info,
        "hackathon": "BNB x CMC Hackathon Track 2",
    }

    with open("bnb_registration.json", "w") as f:
        json.dump(registration, f, indent=2)

    print("Registration saved to: bnb_registration.json")
    return registration


if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  BNB AI AGENT SDK — AAE ON-CHAIN REGISTRATION")
    print("  ERC-8004 Agent Identity — BSC Testnet")
    print("=" * 65)
    print()

    try:
        wallet = setup_wallet()

        print(f"  IMPORTANT: Fund this address with testnet BNB before proceeding:")
        print(f"  Address: {wallet.address}")
        print(f"  Faucet : https://testnet.bnbchain.org/faucet-smart")
        print()

        funded = input("  Have you funded the wallet? (yes/no): ").strip().lower()

        if funded != "yes":
            print()
            print("  Please fund the wallet first, then run this script again.")
            print(f"  Wallet address: {wallet.address}")
            print("  Faucet: https://testnet.bnbchain.org/faucet-smart")
            exit(0)

        result, sdk = register_aae_agent(wallet)
        agent_info = verify_registration(sdk, result["agentId"])
        registration = save_registration(wallet.address, result, agent_info)

        print("=" * 65)
        print("  BNB AI AGENT SDK INTEGRATION COMPLETE")
        print("=" * 65)
        print(f"  AAE is now a registered on-chain AI agent")
        print(f"  Agent ID : {result['agentId']}")
        print(f"  TX Hash  : {result['transactionHash']}")
        print(f"  Explorer : https://testnet.bscscan.com/tx/{result['transactionHash']}")
        print()

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("If this is a wallet error, add to your .env file:")
        print("  BNB_WALLET_PASSWORD=aae-hackathon-2026")
        print("  BNB_PRIVATE_KEY=  (leave blank to auto-generate)")