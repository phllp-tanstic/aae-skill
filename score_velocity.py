import requests
from dotenv import load_dotenv
from fetch_narratives import fetch_narratives
import os

load_dotenv()

def score_velocity(narrative):
    """
    Computes a velocity score 0-100 for a narrative.

    High score = attention growing faster than price.
    This is the core arbitrage signal.

    Components:
    - Volume surge score (40 points max)
    - Market cap momentum score (30 points max)
    - Divergence bonus: volume >> price (30 points max)
    """

    vol_change = narrative["volume_change_24h"]
    mcap_change = narrative["market_cap_change_24h"]
    price_change = narrative["avg_change_24h"]

    # --- Component 1: Volume surge (0-40 points) ---
    # Volume change of 100%+ = full 40 points
    vol_score = min(40, (vol_change / 100) * 40)
    vol_score = max(0, vol_score)

    # --- Component 2: Market cap momentum (0-30 points) ---
    # Mcap change of 20%+ = full 30 points
    mcap_score = min(30, (mcap_change / 20) * 30)
    mcap_score = max(0, mcap_score)

    # --- Component 3: Divergence bonus (0-30 points) ---
    # The key insight: volume growing FASTER than price = early signal
    # If volume_change >> price_change, attention hasn't priced in yet
    divergence = vol_change - abs(price_change)
    divergence_score = min(30, (divergence / 80) * 30)
    divergence_score = max(0, divergence_score)

    total = round(vol_score + mcap_score + divergence_score, 2)

    return {
        "name": narrative["name"],
        "velocity_score": total,
        "vol_score": round(vol_score, 2),
        "mcap_score": round(mcap_score, 2),
        "divergence_score": round(divergence_score, 2),
        "avg_change_24h": narrative["avg_change_24h"],
        "volume_change_24h": narrative["volume_change_24h"],
        "market_cap_change_24h": narrative["market_cap_change_24h"],
        "num_tokens": narrative["num_tokens"],
    }


def score_all_narratives(limit=10):
    """Fetch narratives and score them all, sorted by velocity."""
    narratives = fetch_narratives(limit)
    scored = [score_velocity(n) for n in narratives]
    scored.sort(key=lambda x: x["velocity_score"], reverse=True)
    return scored


if __name__ == "__main__":
    print("Scoring narrative velocity...\n")
    scored = score_all_narratives(10)

    print(f"{'Rank':<5} {'Narrative':<30} {'Score':<8} {'Vol':<8} {'MCap':<8} {'Div':<8}")
    print("-" * 70)

    for i, n in enumerate(scored, 1):
        print(
            f"{i:<5} "
            f"{n['name']:<30} "
            f"{n['velocity_score']:<8} "
            f"{n['vol_score']:<8} "
            f"{n['mcap_score']:<8} "
            f"{n['divergence_score']:<8}"
        )

    print()
    print("Top narrative by velocity:", scored[0]["name"])
    print("Velocity score:", scored[0]["velocity_score"], "/ 100")
    print()
    print("Divergence insight:")
    print(f"  Volume change: {scored[0]['volume_change_24h']}%")
    print(f"  Price change:  {scored[0]['avg_change_24h']}%")
    print(f"  Gap (attention vs price): {round(scored[0]['volume_change_24h'] - abs(scored[0]['avg_change_24h']), 2)}%")