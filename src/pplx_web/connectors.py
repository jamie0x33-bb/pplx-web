from __future__ import annotations

import json
import time
import urllib.request
import urllib.error

from .config import Runtime
from .trace import Recorder


class ConnectorError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def _request(rt: Runtime, path: str, *, method: str = "GET", recorder: Recorder | None = None) -> dict:
    url = f"{rt.connector_base_url}{path}"
    headers = {"content-type": "application/json"}
    headers.update(rt.bearer_header())
    if rt.target_base_url:
        headers["x-base-url"] = rt.target_base_url

    req = urllib.request.Request(url, method=method, headers=headers)

    entry = recorder.begin(req) if recorder else None
    start = time.monotonic()

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            if entry:
                recorder.end(
                    entry,
                    status=resp.status,
                    headers=dict(resp.headers),
                    body=body,
                    elapsed_ms=(time.monotonic() - start) * 1000,
                )
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode(errors="replace")[:500]
        if entry:
            recorder.fail(entry, f"{exc.code}: {err_body}")
        raise ConnectorError(err_body, status=exc.code) from None
    except Exception as exc:
        if entry:
            recorder.fail(entry, str(exc))
        raise ConnectorError(str(exc)) from None


def list_connectors(rt: Runtime, *, recorder: Recorder | None = None) -> list[dict]:
    result = _request(rt, "/connectors", recorder=recorder)
    return result.get("connectors", result if isinstance(result, list) else [])


def preflight(rt: Runtime, connector: str, *, recorder: Recorder | None = None) -> dict:
    return _request(rt, f"/connectors/{connector}/status", recorder=recorder)
