"""
AAE FastAPI Backend
====================
Serves the AAE pipeline output to the live dashboard.
Run with: uvicorn api_server:app --reload --port 8000
"""

import json
import glob
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Attention Arbitrage Engine API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_latest_output():
    """Load the most recent AAE output file."""
    output_files = glob.glob("aae_output_*.json")
    if output_files:
        latest = max(output_files, key=os.path.getctime)
        with open(latest, "r") as f:
            return json.load(f), latest
    return None, None


def load_backtest_results():
    """Load backtest results if available."""
    if os.path.exists("backtest_results.json"):
        with open("backtest_results.json", "r") as f:
            return json.load(f)
    return {}


def load_bnb_registration():
    """Load BNB on-chain registration."""
    if os.path.exists("bnb_registration.json"):
        with open("bnb_registration.json", "r") as f:
            return json.load(f)
    return {}


def load_twak_intelligence():
    """Load TWAK price and signing data."""
    if os.path.exists("twak_intelligence.json"):
        with open("twak_intelligence.json", "r") as f:
            return json.load(f)
    return {}


def load_mcp_results():
    """Load CMC MCP integration results."""
    if os.path.exists("cmc_mcp_results.json"):
        with open("cmc_mcp_results.json", "r") as f:
            return json.load(f)
    return {}


@app.get("/")
def root():
    return {"engine": "Attention Arbitrage Engine v2.0", "status": "running"}


@app.get("/status")
def status():
    """Quick health check for dashboard connection test."""
    data, filename = load_latest_output()
    return {
        "status": "online",
        "engine": "Attention Arbitrage Engine v2.0",
        "last_run": filename,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/dashboard")
def dashboard():
    """
    Full dashboard data endpoint.
    Returns everything the live dashboard needs in one call.
    """
    data, filename = load_latest_output()
    backtest = load_backtest_results()
    bnb_reg = load_bnb_registration()
    twak = load_twak_intelligence()
    mcp = load_mcp_results()

    if not data:
        return JSONResponse(
            status_code=404,
            content={
                "error": "No AAE output found. Run python aae_skill.py first.",
                "hint": "Run: python aae_skill.py",
            },
        )

    market_context = data.get("market_context", {})
    rotation = data.get("rotation_forecast", {})
    specs = data.get("strategy_specs", [])

    classifications = []
    for spec in specs:
        classifications.append({
            "narrative": spec.get("narrative"),
            "lifecycle_stage": spec.get("lifecycle_stage"),
            "confidence": spec.get("confidence"),
            "opportunity_score": spec.get("opportunity_score"),
            "risk_level": spec.get("risk_level"),
            "ai_reasoning": spec.get("ai_reasoning", ""),
            "signal_data": spec.get("signal_data", {}),
            "strategy": spec.get("strategy", {}),
            "backtestable_assets": spec.get("backtestable_assets", []),
            "spec_id": spec.get("spec_id"),
            "generated_at": spec.get("generated_at"),
            "bnb_execution_context": spec.get("bnb_execution_context", {}),
            "estimated_half_life_days": spec.get("estimated_half_life_days"),
            "attention_decay_probability": spec.get("attention_decay_probability"),
            "historical_analog": spec.get("historical_analog", {}),
        })

    twak_prices = twak.get("live_prices", {})
    bnb_price = twak_prices.get("BNB", {}).get("price_usd", 0)
    eth_price = twak_prices.get("ETH", {}).get("price_usd", 0)
    btc_price = twak_prices.get("BTC", {}).get("price_usd", 0)

    trending_bnb = twak.get("trending_bnb", [])[:5]
    signed_specs = twak.get("signed_strategy_specs", [])

    backtest_summary = []
    for spec_id, result in backtest.items():
        for asset_result in result.get("asset_results", []):
            backtest_summary.append({
                "spec_id": spec_id,
                "narrative": result.get("narrative"),
                "lifecycle_stage": result.get("lifecycle_stage"),
                **asset_result,
            })

    return {
        "generated_at": data.get("generated_at"),
        "source_file": filename,
        "market_context": market_context,
        "rotation_forecast": rotation,
        "strategy_specs": classifications,
        "backtest_results": backtest_summary,
        "integrations": {
            "cmc": {
                "status": "connected",
                "endpoints_used": 6,
                "mcp_tools": mcp.get("total_calls", 0),
                "mcp_successful": mcp.get("successful_calls", 0),
                "last_updated": mcp.get("generated_at", ""),
            },
            "bnb": {
                "status": "registered",
                "agent_id": bnb_reg.get("agent_id", "1345"),
                "network": bnb_reg.get("network", "BSC Testnet"),
                "transaction_hash": bnb_reg.get("transaction_hash", ""),
                "registry": bnb_reg.get("erc8004_registry", ""),
            },
            "twak": {
                "status": "connected",
                "version": "0.18.0",
                "bnb_price": round(bnb_price, 2),
                "eth_price": round(eth_price, 2),
                "btc_price": round(btc_price, 0),
                "trending_bnb": trending_bnb,
                "signed_specs": len(signed_specs),
                "wallet_address": signed_specs[0].get("signed_by", "") if signed_specs else "",
                "latest_signature": signed_specs[0] if signed_specs else {},
            },
        },
    }


@app.post("/run")
async def run_pipeline():
    """
    Trigger a full AAE pipeline run.
    Runs aae_skill.py as a subprocess and returns fresh results.
    """
    import subprocess as _sp

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pipeline run triggered via dashboard...")

    venv_python = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "venv", "Scripts", "python.exe"
    )
    python_exe = venv_python if os.path.exists(venv_python) else __import__('sys').executable
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "aae_skill.py"
    )
    work_dir = os.path.dirname(os.path.abspath(__file__))

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    print(f"  Using Python: {python_exe}")
    print(f"  Running: {script_path}")

    def run_blocking():
        return _sp.run(
            [python_exe, script_path],
            capture_output=True,
            timeout=120,
            cwd=work_dir,
            env=env,
        )

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_blocking)

        stdout_text = result.stdout.decode("utf-8", errors="replace")
        stderr_text = result.stderr.decode("utf-8", errors="replace")

        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Pipeline completed successfully")
            data, filename = load_latest_output()
            return {
                "status": "success",
                "message": "Pipeline completed successfully",
                "output_file": filename,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Pipeline error: {stderr_text[:300]}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": stderr_text[:500] or stdout_text[:500]},
            )

    except Exception as e:
        import traceback
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Exception: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )

    except Exception as e:
        import traceback
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Exception: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)},
        )

    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={
                "status": "timeout",
                "message": "Pipeline timed out after 120 seconds",
            },
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Exception in /run:")
        print(tb)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e), "traceback": tb},
        )