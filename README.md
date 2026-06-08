\# Attention Arbitrage Engine (AAE)

\### BNB x CMC Hackathon — Track 2: Strategy Skills



> An AI-powered CMC Skill that identifies emerging crypto narratives before price discovery occurs, classifies their lifecycle stage, and generates structured, backtestable trading strategies from attention, news, and on-chain signals.

\---



\## What It Does



Most traders discover narratives after the market has already priced them in. The \*\*Attention Arbitrage Engine\*\* identifies the gap between \*\*attention growth\*\* and \*\*price appreciation\*\*, surfacing emerging narratives where interest is accelerating but valuation remains largely unchanged.



By combining \*\*CoinMarketCap\*\* narrative trends, news signals, and market activity, the engine measures narrative momentum, classifies each narrative into a lifecycle stage (Emergence, Acceleration, Saturation, or Decay), and generates a complete, backtestable trading strategy specification with defined entry, exit, and risk parameters.



\*\*The core insight is simple:\*\* attention tends to move before price. When a narrative’s volume grows by 150%+ while associated token prices have only moved 5%, the resulting divergence often signals an early-stage opportunity before broader market discovery and capital inflows occur.

\---



\## Pipeline Architecture

CMC Live Data

│

▼

\[1] Narrative Fetcher       → Top trending categories from CMC

│

▼

\[2] Velocity Scorer         → Attention vs price divergence score (0-100)

│

▼

\[3] Divergence Checker      → Signal strength classification

│

▼

\[4] Macro Enrichment        → BTC dominance regime context

│

▼

\[5] AI Lifecycle Classifier → EMERGENCE / ACCELERATION / SATURATION / DECAY

│

▼

\[6] Strategy Spec Generator → Backtestable strategy specification

│

▼

\[7] Backtester              → Historical validation with Sharpe, return, drawdown



\---



\## CMC Data Sources Used



| CMC Tool | Purpose |

|---|---|

| `/v1/cryptocurrency/categories` | Trending narrative discovery |

| `/v1/global-metrics/quotes/latest` | Macro regime detection |

| `/v1/cryptocurrency/listings/latest` | Token price and volume data |

| `/v1/cryptocurrency/category` | Token basket per narrative |

| `/v1/cryptocurrency/quotes/latest` | Per-token enrichment |

| `/v1/cryptocurrency/trending/gainers-losers` | Momentum confirmation |



\---



\## Lifecycle Stages



| Stage | Signal | Strategy |

|---|---|---|

| 🟢 EMERGENCE | Volume surging, price flat | Early accumulation, 2-4% position |

| 🟡 ACCELERATION | Volume + price both rising | Momentum ride, 3-5% position |

| 🟠 SATURATION | Price moved, volume slowing | Reduce or fade |

| 🔴 DECAY | Both declining | Exit or avoid |



\---



\## Example Output



```json

{

&#x20; "spec\_id": "AAE-20260608-2322-EME",

&#x20; "narrative": "Filesharing",

&#x20; "lifecycle\_stage": "EMERGENCE",

&#x20; "confidence": 0.68,

&#x20; "opportunity\_score": 80,

&#x20; "risk\_level": "HIGH",

&#x20; "strategy": {

&#x20;   "type": "Early Position Accumulation",

&#x20;   "thesis": "Narrative attention accelerating faster than price.",

&#x20;   "entry\_rule": "velocity\_score > 60 AND volume\_change\_24h > 100% AND price\_change < 15%",

&#x20;   "entry\_trigger": "Buy on next daily open after signal confirmation",

&#x20;   "position\_size": "2-4% of portfolio",

&#x20;   "stop\_loss": "-15% from entry price",

&#x20;   "time\_horizon": "7-21 days"

&#x20; },

&#x20; "backtestable\_assets": \["FIL", "AR", "RIF"],

&#x20; "market\_context": {

&#x20;   "regime": "BTC\_DOMINANCE",

&#x20;   "btc\_dominance": 58.13

&#x20; }

}

```



\---



\## Backtest Results (30-day window)



| Asset | Narrative | Return | Max Drawdown | Sharpe | Result |

|---|---|---|---|---|---|

| MRVLX | xStocks Ecosystem | +33.39% | 7.48% | 9.14 | ✅ PASS |

| RIF | Filesharing | +15.94% | 16.46% | 2.47 | ✅ PASS |

| FIL | Filesharing | -11.87% | 11.87% | -7.08 | 🛑 STOP LOSS |

| AR | Filesharing | -12.90% | 12.90% | -4.71 | 🛑 STOP LOSS |



> Stop losses firing on FIL and AR confirm the risk management works as designed.

> The engine correctly flagged BTC dominance headwind and reduced position sizing.



\---



\## How To Run



\### 1. Clone the repo

```bash

git clone https://github.com/phllp-tanstic/aae-skill.git

cd aae-skill

```



\### 2. Create virtual environment

```bash

python -m venv venv

venv\\Scripts\\activate        # Windows

source venv/bin/activate     # Mac/Linux

```



\### 3. Install dependencies

```bash

pip install anthropic groq requests python-dotenv pandas yfinance

```



\### 4. Set up API keys

Create a `.env` file:

CMC\_API\_KEY=your\_coinmarketcap\_key

GROQ\_API\_KEY=your\_groq\_key





\### 5. Run the engine

```bash

python aae\_skill.py

```



\### 6. Run the backtester

```bash

python backtest\_spec.py

```



\---



\## File Structure

aae-skill/

├── aae\_skill.py            # Master entry point — run this

├── fetch\_narratives.py     # CMC narrative data fetcher

├── score\_velocity.py       # Velocity scoring algorithm

├── check\_divergence.py     # Divergence signal detector

├── enrich\_narratives.py    # Macro regime enrichment

├── classify\_lifecycle.py   # AI lifecycle classifier (Groq/Claude)

├── generate\_strategy.py    # Strategy spec generator

├── backtest\_spec.py        # Historical backtester

├── strategy\_output.json    # Sample strategy specs

├── backtest\_results.json   # Sample backtest results

├── .env                    # API keys (not committed)

└── README.md



\---



\## The Arbitrage Logic



The velocity score is computed as:

velocity\_score = vol\_surge\_score (0-40)

\+ mcap\_momentum\_score (0-30)

\+ divergence\_bonus (0-30)

divergence\_bonus = volume\_change - abs(price\_change)



High divergence bonus = attention growing faster than price = early signal.



\---



\## Built With



\- \*\*CoinMarketCap Pro API\*\* — 6 endpoints for narrative and market data

\- \*\*Groq (LLaMA 3.3 70B)\*\* — AI lifecycle classification

\- \*\*Python\*\* — pipeline orchestration

\- \*\*yfinance\*\* — historical price data for backtesting

\- \*\*pandas\*\* — data processing



\---



\## Hackathon



\*\*BNB x CMC Hackathon — Track 2: Strategy Skills\*\*

Built for the CMC Skills Marketplace.

Submission: dorahacks.io/hackathon/bnbhack-twt-cmc.

