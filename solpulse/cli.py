"""Command-line interface for generating a Solana Ecosystem Pulse snapshot."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from solpulse.artifacts import write_artifacts
from solpulse.collector import collect_snapshot
from solpulse.market import HttpJsonClient
from solpulse.rpc import HttpRpcClient, RpcError

DEFAULT_ENDPOINT = "https://api.mainnet-beta.solana.com"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="solpulse",
        description="Generate auditable JSON, Markdown, and HTML Solana network reports.",
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Solana JSON-RPC endpoint")
    parser.add_argument("--output", default="output", help="Artifact output directory")
    parser.add_argument("--timeout", type=float, default=30.0, help="RPC timeout in seconds")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    rpc_factory: Callable[..., Any] = HttpRpcClient,
    economic_factory: Callable[..., Any] = HttpJsonClient,
    generated_at: str | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    try:
        rpc = rpc_factory(args.endpoint, timeout=args.timeout)
        economic_client = economic_factory(timeout=args.timeout)
        snapshot = collect_snapshot(
            rpc,
            source=args.endpoint,
            generated_at=generated_at,
            economic_client=economic_client,
        )
        paths = write_artifacts(snapshot, Path(args.output))
    except (RpcError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"solpulse: generation failed: {exc}", file=sys.stderr)
        return 1

    metrics = snapshot["metrics"]
    print(
        f"Generated snapshot at {snapshot['generated_at']} · "
        f"slot {metrics['slot']:,} · TPS {metrics['tps']:,.2f}"
    )
    for name, path in paths.items():
        print(f"{name}: {path.resolve()}")
    return 0
