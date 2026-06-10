"""
CMC Agent Hub — Skill Hub MCP Integration
==========================================
Connects AAE to the official CMC Skill Hub MCP endpoint.
Uses find_skill and execute_skill to demonstrate Agent Hub usage.

MCP Endpoint : https://mcp.coinmarketcap.com/skill-hub/stream
Auth Header  : X-CMC-MCP-API-KEY
Transport    : Streamable HTTP

Tools:
- find_skill    → Discover relevant CMC Skills for AAE signals
- execute_skill → Execute pre-built CMC Skills for market data

BNB x CMC Hackathon — CMC Agent Hub Special Prize
"""

import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CMC_SKILL_HUB_URL = "https://mcp.coinmarketcap.com/skill-hub/stream"
CMC_MCP_URL = "https://mcp.coinmarketcap.com/mcp"
CMC_API_KEY = os.getenv("CMC_API_KEY")

MCP_HEADERS = {
    "X-CMC-MCP-API-KEY": CMC_API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def parse_mcp_response(response):
    """Parse MCP response — handles both JSON and SSE stream formats."""
    raw = response.text.strip()
    if raw.startswith("data:"):
        for line in raw.split("\n"):
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str and data_str != "[DONE]":
                    try:
                        chunk = json.loads(data_str)
                        if "result" in chunk:
                            return chunk["result"], None
                    except json.JSONDecodeError:
                        pass
        return {"raw": raw[:500]}, None
    else:
        try:
            data = response.json()
            if "result" in data:
                return data["result"], None
            elif "error" in data:
                return None, str(data["error"])
            return data, None
        except Exception as e:
            return {"raw": raw[:500]}, None


def skill_hub_call(method, params=None):
    """Call CMC Skill Hub MCP endpoint."""
    if params is None:
        params = {}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    try:
        response = requests.post(
            CMC_SKILL_HUB_URL,
            headers=MCP_HEADERS,
            json=payload,
            timeout=60,
        )
        if response.status_code == 200:
            return parse_mcp_response(response)
        return None, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return None, str(e)


def data_mcp_call(method, params=None):
    """Call CMC Data MCP endpoint."""
    if params is None:
        params = {}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    try:
        response = requests.post(
            CMC_MCP_URL,
            headers=MCP_HEADERS,
            json=payload,
            timeout=30,
        )
        if response.status_code == 200:
            return parse_mcp_response(response)
        return None, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return None, str(e)


def find_skill(query):
    """Use find_skill to discover CMC Skills relevant to AAE."""
    result, error = skill_hub_call(
        "tools/call",
        {
            "name": "find_skill",
            "arguments": {"query": query},
        },
    )
    return result, error


def execute_skill(unique_name, parameters=None):
    """Execute a CMC Skill by name."""
    if parameters is None:
        parameters = {}
    result, error = skill_hub_call(
        "tools/call",
        {
            "name": "execute_skill",
            "arguments": {
                "unique_name": unique_name,
                "parameters": parameters,
            },
        },
    )
    return result, error


def list_mcp_tools(endpoint_url):
    """List tools available on an MCP endpoint."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    try:
        response = requests.post(
            endpoint_url, headers=MCP_HEADERS, json=payload, timeout=15
        )
        if response.status_code == 200:
            result, _ = parse_mcp_response(response)
            return result
        return None
    except Exception:
        return None


def run_cmc_mcp_integration():
    """
    Full CMC Agent Hub MCP integration.
    Demonstrates Skill Hub + Data MCP usage.
    """
    print("\n" + "=" * 65)
    print("  CMC AGENT HUB — MCP INTEGRATION")
    print("=" * 65)
    print(f"  Skill Hub : {CMC_SKILL_HUB_URL}")
    print(f"  Data MCP  : {CMC_MCP_URL}")
    print(f"  Transport : Streamable HTTP")
    print()

    results = {}

    print("  ── Skill Hub MCP ──────────────────────────────────────")
    print()

    print("  Step 1: List Skill Hub tools")
    tools = list_mcp_tools(CMC_SKILL_HUB_URL)
    if tools:
        tool_list = tools.get("tools", [])
        print(f"  ✅ Connected — {len(tool_list)} tools available")
        for t in tool_list:
            name = t.get("name", str(t)) if isinstance(t, dict) else str(t)
            print(f"     • {name}")
        results["skill_hub_tools"] = "SUCCESS"
    else:
        print("  ⚠️  Could not list tools — attempting direct calls")
        results["skill_hub_tools"] = "UNAVAILABLE"
    print()

    print("  Step 2: find_skill — discover narrative/market skills")
    queries = [
        "narrative momentum crypto",
        "btc price market overview",
        "trending crypto tokens",
    ]
    found_skills = []
    for query in queries:
        print(f"  Query: '{query}'")
        result, error = find_skill(query)
        if result:
            content = result.get("content", [])
            text = content[0].get("text", str(result)) if content else str(result)
            print(f"  ✅ Result: {text[:150]}...")
            results[f"find_skill_{query[:20]}"] = "SUCCESS"
            found_skills.append({"query": query, "result": text[:300]})
        else:
            print(f"  ⚠️  {error}")
            results[f"find_skill_{query[:20]}"] = f"FAILED: {error}"
    print()

    print("  Step 3: execute_skill — run market overview skill")
    skill_attempts = [
        ("daily_market_overview", {"preview": True}),
        ("btc_cross_asset_correlation", {"preview": True}),
        ("crypto_macro_overview", {"preview": True}),
    ]
    executed_skills = []
    for skill_name, params in skill_attempts:
        print(f"  Executing: {skill_name}")
        result, error = execute_skill(skill_name, params)
        if result:
            content = result.get("content", [])
            text = content[0].get("text", str(result)) if content else str(result)
            print(f"  ✅ Success: {text[:150]}...")
            results[f"execute_{skill_name}"] = "SUCCESS"
            executed_skills.append({"skill": skill_name, "result": text[:300]})
            break
        else:
            print(f"  ⚠️  {error}")
            results[f"execute_{skill_name}"] = f"FAILED: {error}"
    print()

    print("  ── Data MCP ───────────────────────────────────────────")
    print()

    print("  Step 4: List Data MCP tools")
    data_tools = list_mcp_tools(CMC_MCP_URL)
    if data_tools:
        tool_list = data_tools.get("tools", [])
        print(f"  ✅ Connected — {len(tool_list)} data tools available")
        for t in tool_list[:6]:
            name = t.get("name", str(t)) if isinstance(t, dict) else str(t)
            print(f"     • {name}")
        results["data_mcp_tools"] = "SUCCESS"
    else:
        print("  ⚠️  Data MCP tools unavailable")
        results["data_mcp_tools"] = "UNAVAILABLE"
    print()

    print("  Step 5: trending_crypto_narratives via Data MCP")
    result, error = data_mcp_call(
        "tools/call",
        {"name": "trending_crypto_narratives", "arguments": {}},
    )
    if result:
        content = result.get("content", [])
        text = content[0].get("text", str(result)) if content else str(result)
        print(f"  ✅ Success: {text[:200]}...")
        results["trending_narratives_mcp"] = "SUCCESS"
    else:
        print(f"  ⚠️  {error}")
        results["trending_narratives_mcp"] = f"FAILED: {error}"
    print()

    successful = sum(1 for v in results.values() if v == "SUCCESS")
    total = len(results)

    output = {
        "integration": "CMC Agent Hub MCP",
        "skill_hub_endpoint": CMC_SKILL_HUB_URL,
        "data_mcp_endpoint": CMC_MCP_URL,
        "transport": "Streamable HTTP",
        "generated_at": datetime.now().isoformat(),
        "tools_called": list(results.keys()),
        "results": results,
        "found_skills": found_skills,
        "executed_skills": executed_skills,
        "successful_calls": successful,
        "total_calls": total,
        "status": "CONNECTED" if successful > 0 else "ENDPOINT_UNREACHABLE",
        "note": (
            "AAE uses both CMC REST API (6 direct endpoints) and the "
            "Agent Hub MCP layer (Skill Hub + Data MCP) for full "
            "CMC Agent Hub coverage."
        ),
    }

    with open("cmc_mcp_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"  {'─'*61}")
    print(f"  MCP calls successful : {successful} / {total}")
    print(f"  Status               : {output['status']}")
    print(f"  Results saved        : cmc_mcp_results.json")
    print("  CMC MCP integration complete.")

    return output


if __name__ == "__main__":
    run_cmc_mcp_integration()