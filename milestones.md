# AAE Development Milestones

This document records the development progress of the Attention Arbitrage Engine (AAE) from initial environment setup through final hackathon submission.

## Phase 1 — Environment & Foundations

The development environment was established on Python 3.11 with all required dependencies installed and verified. CoinMarketCap Pro API access was configured and validated across six endpoints. Groq API access was provisioned using LLaMA 3.3 70B as the primary reasoning model. Project infrastructure was initialized through a dedicated GitHub repository and DoraHacks registration.

Key dependencies included `groq`, `anthropic`, `requests`, `python-dotenv`, `pandas`, `yfinance`, `mcp`, `bnbagent`, `web3`, `fastapi`, and `uvicorn`.

## Phase 2 — Core Data Pipeline

The narrative intelligence pipeline was implemented using CoinMarketCap category data as the primary data source.

`fetch_narratives.py` established integration with the CoinMarketCap Categories API. `score_velocity.py` introduced the velocity scoring framework combining volume surge, market capitalization momentum, and divergence signals. `check_divergence.py` implemented attention versus price divergence detection, while `enrich_narratives.py` added BTC dominance regime context.

Relative attention alpha was introduced to measure narrative performance against overall market activity. The final architecture was optimized as a single-pass pipeline, eliminating duplicate API requests and redundant computation.

## Phase 3 — AI Intelligence Layer

The AI reasoning layer was implemented using Groq-hosted LLaMA 3.3 70B.

`classify_lifecycle.py` introduced a five-stage narrative lifecycle framework consisting of EMERGENCE, EARLY_ACCELERATION, LATE_ACCELERATION, SATURATION, and DECAY. The classifier was extended with narrative half-life estimation, historical analog matching, and structured reasoning generation.

`predict_rotation.py` added capital rotation forecasting, while `generate_strategy.py` transformed classified narratives into parameterized strategy specifications with regime-aware adjustments. `backtest_spec.py` introduced historical validation through return, drawdown, and Sharpe ratio analysis. These components were unified through `aae_skill.py`, which serves as the primary orchestration layer.

## Phase 4 — Sponsor Integrations

The project integrated all three sponsor ecosystems.

The BNB AI Agent SDK was used to register AAE through the ERC-8004 agent registry, resulting in Agent ID 1345 on BSC Testnet. Agent registry interaction and job simulation workflows were successfully demonstrated.

Trust Wallet Agent Kit integration was implemented using the official CLI and developer credentials. The integration supports ECDSA secp256k1 signing, self-custodial wallet operations, live price retrieval, BNB ecosystem trend discovery, and PancakeSwap V3 signed swap intent generation.

CoinMarketCap Agent Hub integrations included MCP connectivity through Streamable HTTP, Skill Hub execution workflows, and x402 payment protocol demonstrations. Supporting integration modules were implemented through `bnb_integration.py`, `cmc_mcp_integration.py`, `trust_wallet_integration.py`, and `x402_simulation.py`.

## Phase 5 — Live Dashboard

A live monitoring interface was developed using FastAPI and a browser-based dashboard.

`api_server.py` exposes pipeline output through a local API endpoint, while `dashboard.html` provides real-time visualization of narrative intelligence results. The dashboard supports full pipeline execution, automatic refresh, sponsor integration status monitoring, and display of TWAK-signed strategy artifacts.

## Phase 6 — Polish & Submission

Final development focused on documentation, stability, and integration refinement.

Production documentation was completed, including the project README, requirements specification, and milestone records. Historical validation datasets were audited to remove symbol collisions, including the MRVLX ticker conflict. Trust Wallet Agent Kit integration was expanded from signing-only functionality to execution-layer support through signed swap intents. The BNB AI Agent SDK implementation was extended beyond registration to demonstrate agent capabilities and execution context workflows.

Node.js was upgraded from version 20 to version 24 to resolve Trust Wallet Agent Kit ESM compatibility issues. Final validation, testing, and documentation reviews were completed prior to submission.
