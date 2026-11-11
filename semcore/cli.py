"""Command line interface: fetch, build, refresh, validate, serve."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .config import DOCS_DIR, ROOT, SITE_URL, SITE_VERSION
from .market import fetch_snapshot, load_snapshot, save_snapshot
from .taxonomy import Taxonomy
from .universe import load_universe


def _print(message: str = "") -> None:
    print(message, flush=True)


def cmd_fetch(args: argparse.Namespace) -> int:
    taxonomy = Taxonomy.load()
    companies = load_universe(taxonomy=taxonomy)
    previous = load_snapshot()
    _print(f"Fetching {len(companies)} companies from Eastmoney (workers={args.workers})…")
    snapshot = fetch_snapshot(companies, taxonomy, previous=previous, max_workers=args.workers)
    save_snapshot(snapshot)
    coverage = snapshot["coverage"]
    _print(f"Coverage: {coverage['priced']}/{coverage['total']} ({coverage['ratio'] * 100:.1f}%)")
    _print(f"News items: {len(snapshot.get('news') or [])}")
    if snapshot.get("errors"):
        _print("Errors:")
        for error in snapshot["errors"][:20]:
            _print(f"  - {error}")
    _print(f"Snapshot written to data/snapshots/latest.json ({snapshot['dataset']})")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    from .build import SiteBuilder

    snapshot = None
    if args.snapshot:
        snapshot = load_snapshot(Path(args.snapshot))
    builder = SiteBuilder(snapshot=snapshot, output=Path(args.out) if args.out else None)
    manifest = builder.build()
    _print(f"Built {manifest['pages']} files into {builder.output}")
    _print(f"Site URL: {SITE_URL}")
    _print(f"Snapshot: {builder.snapshot.get('generated_at')} ({builder.snapshot.get('dataset')})")
    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    code = cmd_fetch(args)
    if code:
        return code
    return cmd_build(args)


def cmd_validate(args: argparse.Namespace) -> int:
    from .validate import validate_all

    errors = validate_all(docs_dir=Path(args.docs) if args.docs else DOCS_DIR, data_only=args.data_only)
    if errors:
        _print(f"Validation failed with {len(errors)} issue(s):")
        for error in errors:
            _print(f"  - {error}")
        return 1
    _print("Validation passed.")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    directory = Path(args.dir) if args.dir else DOCS_DIR
    if not (directory / "index.html").exists():
        _print(f"No build found in {directory}. Run `python -m semcore build` first.")
        return 1

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **handler_kwargs):
            super().__init__(*handler_args, directory=str(directory), **handler_kwargs)

        def log_message(self, fmt, *log_args):  # keep the console quiet
            return

    port = args.port
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        _print(f"Serving {directory} at http://127.0.0.1:{port}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            _print("\nStopped.")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    snapshot = load_snapshot() or {}
    taxonomy = Taxonomy.load()
    companies = load_universe(taxonomy=taxonomy)
    _print(json.dumps(
        {
            "version": SITE_VERSION,
            "site_url": SITE_URL,
            "companies": len(companies),
            "stages": len(taxonomy.stages),
            "snapshot": {
                "generated_at": snapshot.get("generated_at"),
                "dataset": snapshot.get("dataset"),
                "coverage": snapshot.get("coverage"),
                "fx_source": (snapshot.get("fx") or {}).get("source"),
                "news": len(snapshot.get("news") or []),
            },
            "docs_exists": (DOCS_DIR / "index.html").exists(),
            "root": str(ROOT),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="semcore", description="SiliconScope build tooling")
    parser.add_argument("--version", action="version", version=f"SiliconScope {SITE_VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="Fetch a fresh market snapshot (network required)")
    fetch.add_argument("--workers", type=int, default=6)
    fetch.set_defaults(func=cmd_fetch)

    build = sub.add_parser("build", help="Render the static site from the latest snapshot")
    build.add_argument("--snapshot", help="Path to a snapshot JSON file")
    build.add_argument("--out", help="Output directory (default: docs/)")
    build.set_defaults(func=cmd_build)

    refresh = sub.add_parser("refresh", help="Fetch and build in one step")
    refresh.add_argument("--workers", type=int, default=6)
    refresh.add_argument("--snapshot", help=argparse.SUPPRESS)
    refresh.add_argument("--out", help=argparse.SUPPRESS)
    refresh.set_defaults(func=cmd_refresh)

    validate = sub.add_parser("validate", help="Validate data contracts and generated artifacts")
    validate.add_argument("--docs", help="Docs directory to validate")
    validate.add_argument("--data-only", action="store_true", help="Skip generated artifact checks")
    validate.set_defaults(func=cmd_validate)

    serve = sub.add_parser("serve", help="Serve the built site locally")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--dir", help="Directory to serve")
    serve.set_defaults(func=cmd_serve)

    info = sub.add_parser("info", help="Print repository and snapshot status")
    info.set_defaults(func=cmd_info)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
