from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import load
from .connectors import preflight, list_connectors, ConnectorError
from .trace import Recorder, upload_trace


def _status(args) -> int:
    rt = load()
    info = {
        "version": __version__,
        "in_sandbox": rt.in_sandbox,
        "connector_base_url": rt.connector_base_url,
        "target_base_url": rt.target_base_url,
        "agent_id": rt.agent_id,
        "trace_service": rt.trace_service,
    }
    print(json.dumps(info, indent=2))
    return 0


def _preflight(args) -> int:
    rt = load()
    if not rt.in_sandbox:
        print("not in a sandbox — no proxy token available", file=sys.stderr)
        return 1

    recorder = Recorder() if args.trace else None

    try:
        result = preflight(rt, args.connector, recorder=recorder)
    except ConnectorError as exc:
        print(f"preflight failed: {exc}", file=sys.stderr)
        if recorder:
            path = recorder.save()
            print(f"trace saved: {path}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = result.get("status", "unknown")
        target = result.get("target_base_url", result.get("target", ""))
        print(f"{args.connector}: {status}  target={target}")

    if recorder:
        path = recorder.save()
        print(f"trace saved: {path}")
        try:
            resp = upload_trace(path, rt.trace_service)
            print(f"trace uploaded — trace_id: {resp.get('trace_id', 'unknown')}")
            viewer = resp.get("viewer_url", "")
            if viewer:
                print(f"viewer: {viewer}")
        except Exception as exc:
            print(f"trace upload failed (saved locally): {exc}", file=sys.stderr)

    return 0


def _list(args) -> int:
    rt = load()
    if not rt.in_sandbox:
        print("not in a sandbox", file=sys.stderr)
        return 1

    recorder = Recorder() if args.trace else None
    try:
        items = list_connectors(rt, recorder=recorder)
    except ConnectorError as exc:
        print(f"list failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(items, indent=2))
    else:
        for c in items:
            name = c.get("name", c.get("id", "?"))
            print(f"  {name}")

    if recorder:
        path = recorder.save()
        print(f"trace saved: {path}")
    return 0


def _trace_upload(args) -> int:
    rt = load()
    trace_path = Path(args.file)
    if not trace_path.exists():
        print(f"file not found: {trace_path}", file=sys.stderr)
        return 1

    service = args.service or rt.trace_service
    try:
        result = upload_trace(trace_path, service)
    except Exception as exc:
        print(f"upload failed: {exc}", file=sys.stderr)
        return 1

    trace_id = result.get("trace_id", "unknown")
    viewer = result.get("viewer_url", "")
    print(f"uploaded — trace_id: {trace_id}")
    if viewer:
        print(f"viewer:   {viewer}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="pplx-web",
        description="Browser automation helpers for Perplexity Computer",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("status", help="show runtime environment")
    s.set_defaults(func=_status)

    pf = sub.add_parser("preflight", help="check connector availability")
    pf.add_argument("connector", help="connector name (gmail, google-drive, etc.)")
    pf.add_argument("--trace", action="store_true", help="record HTTP trace")
    pf.add_argument("--json", action="store_true")
    pf.set_defaults(func=_preflight)

    ls = sub.add_parser("list", help="list available connectors")
    ls.add_argument("--trace", action="store_true")
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(func=_list)

    tr = sub.add_parser("trace", help="trace management")
    tr_sub = tr.add_subparsers(dest="trace_command", required=True)
    tu = tr_sub.add_parser("upload", help="upload a trace file")
    tu.add_argument("file", help="path to trace JSON file")
    tu.add_argument("--service", help="override trace service URL")
    tu.set_defaults(func=_trace_upload)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
