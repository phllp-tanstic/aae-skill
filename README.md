# Attention Arbitrage Engine (AAE)
### BNB x CMC Hackathon — Track 2: Strategy Skills

> An AI-powered CMC Skill that identifies emerging crypto narratives before price discovery occurs, classifies their lifecycle stage, and generates structured, backtestable trading strategies from attention, news, and on-chain signals.
---

## What It Does

Most traders discover narratives after the market has already priced them in. The **Attention Arbitrage Engine** identifies the gap between **attention growth** and **price appreciation**, surfacing emerging narratives where interest is accelerating but valuation remains largely unchanged.

By combining **CoinMarketCap** narrative trends, news signals, and market activity, the engine measures narrative momentum, classifies each narrative into a lifecycle stage (Emergence, Acceleration, Saturation, or Decay), and generates a complete, backtestable trading strategy specification with defined entry, exit, and risk parameters.

**The core insight is simple:** attention tends to move before price. When a narrative’s volume grows by 150%+ while associated token prices have only moved 5%, the resulting divergence often signals an early-stage opportunity before broader market discovery and capital inflows occur.
---

## Pipeline Architecture
CMC Live Data
│
▼
[1] Narrative Fetcher       → Top trending categories from CMC
│
▼
[2] Velocity Scorer         → Attention vs price divergence score (0-100)
│
▼
[3] Divergence Checker      → Signal strength classification
│
▼
[4] Macro Enrichment        → BTC dominance regime context
│
▼
[5] AI Lifecycle Classifier → EMERGENCE / ACCELERATION / SATURATION / DECAY
│
▼
[6] Strategy Spec Generator → Backtestable strategy specification
│
▼
[7] Backtester              → Historical validation with Sharpe, return, drawdown

---

## CMC Data Sources Used

| CMC Tool | Purpose |
|---|---|
| `/v1/cryptocurrency/categories` | Trending narrative discovery |
| `/v1/global-metrics/quotes/latest` | Macro regime detection |
| `/v1/cryptocurrency/listings/latest` | Token price and volume data |
| `/v1/cryptocurrency/category` | Token basket per narrative |
| `/v1/cryptocurrency/quotes/latest` | Per-token enrichment |
| `/v1/cryptocurrency/trending/gainers-losers` | Momentum confirmation |

---

## Lifecycle Stages

| Stage | Signal | Strategy |
|---|---|---|
| 🟢 EMERGENCE | Volume surging, price flat | Early accumulation, 2-4% position |
| 🟡 ACCELERATION | Volume + price both rising | Momentum ride, 3-5% position |
| 🟠 SATURATION | Price moved, volume slowing | Reduce or fade |
| 🔴 DECAY | Both declining | Exit or avoid |

---

## Example Output

```json
{
  "spec_id": "AAE-20260608-2322-EME",
  "narrative": "Filesharing",
  "lifecycle_stage": "EMERGENCE",
  "confidence": 0.68,
  "opportunity_score": 80,
  "risk_level": "HIGH",
  "strategy": {
    "type": "Early Position Accumulation",
    "thesis": "Narrative attention accelerating faster than price.",
    "entry_rule": "velocity_score > 60 AND volume_change_24h > 100% AND price_change < 15%",
    "entry_trigger": "Buy on next daily open after signal confirmation",
    "position_size": "2-4% of portfolio",
    "stop_loss": "-15% from entry price",
    "time_horizon": "7-21 days"
  },
  "backtestable_assets": ["FIL", "AR", "RIF"],
  "market_context": {
    "regime": "BTC_DOMINANCE",
    "btc_dominance": 58.13
  }
}
```

---

## Backtest Results (30-day window)

| Asset | Narrative | Return | Max Drawdown | Sharpe | Result |
|---|---|---|---|---|---|
| MRVLX | xStocks Ecosystem | +33.39% | 7.48% | 9.14 | ✅ PASS |
| RIF | Filesharing | +15.94% | 16.46% | 2.47 | ✅ PASS |
| FIL | Filesharing | -11.87% | 11.87% | -7.08 | 🛑 STOP LOSS |
| AR | Filesharing | -12.90% | 12.90% | -4.71 | 🛑 STOP LOSS |

> Stop losses firing on FIL and AR confirm the risk management works as designed.
> The engine correctly flagged BTC dominance headwind and reduced position sizing.

---

## How To Run

### 1. Clone the repo
```bash
git clone https://github.com/phllp-tanstic/aae-skill.git
cd aae-skill
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install anthropic groq requests python-dotenv pandas yfinance
```

### 4. Set up API keys
Create a `.env` file:
CMC_API_KEY=your_coinmarketcap_key
GROQ_API_KEY=your_groq_key


### 5. Run the engine
```bash
python aae_skill.py
```

### 6. Run the backtester
```bash
python backtest_spec.py
```

---

## File Structure
aae-skill/
├── aae_skill.py            # Master entry point — run this
├── fetch_narratives.py     # CMC narrative data fetcher
├── score_velocity.py       # Velocity scoring algorithm
├── check_divergence.py     # Divergence signal detector
├── enrich_narratives.py    # Macro regime enrichment
├── classify_lifecycle.py   # AI lifecycle classifier (Groq/Claude)
├── generate_strategy.py    # Strategy spec generator
├── backtest_spec.py        # Historical backtester
├── strategy_output.json    # Sample strategy specs
├── backtest_results.json   # Sample backtest results
├── .env                    # API keys (not committed)
└── README.md

---

## The Arbitrage Logic

The velocity score is computed as:
velocity_score = vol_surge_score (0-40)
+ mcap_momentum_score (0-30)
+ divergence_bonus (0-30)
divergence_bonus = volume_change - abs(price_change)

High divergence bonus = attention growing faster than price = early signal.

---

## Built With

- **CoinMarketCap Pro API** — 6 endpoints for narrative and market data
- **Groq (LLaMA 3.3 70B)** — AI lifecycle classification
- **Python** — pipeline orchestration
- **yfinance** — historical price data for backtesting
- **pandas** — data processing

---

## Hackathon

**BNB x CMC Hackathon — Track 2: Strategy Skills**
Built for the CMC Skills Marketplace.
Submission: dorahacks.io/hackathon/bnbhack-twt-cmc.