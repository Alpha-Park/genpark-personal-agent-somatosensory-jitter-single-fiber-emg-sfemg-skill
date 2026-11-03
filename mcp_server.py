"""
MCP Server for Somatosensory Jitter Single Fiber EMG (SFEMG) Skill.
Exposes tools for single-pair MCD/MSD calculation and multi-pair clinical study evaluation.
"""

import sys
import json
from typing import Any, Dict, List
from client import SomatosensorySFEMGJitterClient


def format_response(data: Any) -> str:
    return json.dumps(data, indent=2)


def main():
    """Simple FastMCP-compatible stdio JSON-RPC interface."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            continue

        method = req.get("method")
        params = req.get("params", {})
        req_id = req.get("id")

        if method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "compute_single_pair_jitter",
                            "description": "Calculates Mean Consecutive Difference (MCD), Mean Sorted Difference (MSD), drift correction, and impulse blocking for a single muscle fiber potential pair.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target_muscle": {
                                        "type": "string",
                                        "description": "Target muscle name (e.g., extensor_digitorum_communis, frontalis, orbicularis_oculi, biceps_brachii, tibialis_anterior)."
                                    },
                                    "ipi_series_us": {
                                        "type": "array",
                                        "items": {"type": "number"},
                                        "description": "Consecutive interpotential intervals in microseconds (us). Minimum 10 intervals."
                                    },
                                    "blocked_discharges": {
                                        "type": "integer",
                                        "description": "Number of blocked discharges observed in this series (default: 0)."
                                    }
                                },
                                "required": ["ipi_series_us"]
                            }
                        },
                        {
                            "name": "evaluate_multi_pair_study",
                            "description": "Evaluates full SFEMG neuromuscular junction (NMJ) transmission safety factor and pathological classification across multiple motor unit pairs.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target_muscle": {
                                        "type": "string",
                                        "description": "Target muscle name (default: extensor_digitorum_communis)."
                                    },
                                    "pair_records": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "ipi_series_us": {"type": "array", "items": {"type": "number"}},
                                                "blocked_discharges": {"type": "integer"}
                                            },
                                            "required": ["ipi_series_us"]
                                        },
                                        "description": "List of motor unit pair records (minimum 5 pairs)."
                                    }
                                },
                                "required": ["pair_records"]
                            }
                        }
                    ]
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})
            muscle = args.get("target_muscle", "extensor_digitorum_communis")
            client = SomatosensorySFEMGJitterClient(target_muscle=muscle)

            try:
                if name == "compute_single_pair_jitter":
                    series = args.get("ipi_series_us", [])
                    blocked = args.get("blocked_discharges", 0)
                    result = client.compute_single_pair_jitter(series, blocked)
                elif name == "evaluate_multi_pair_study":
                    records = args.get("pair_records", [])
                    result = client.evaluate_multi_pair_study(records)
                else:
                    result = {"error": f"Unknown tool name: {name}"}

                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": format_response(result)}]}
                }) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    main()
