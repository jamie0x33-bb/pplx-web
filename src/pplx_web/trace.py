from __future__ import annotations

import json
import time
import uuid
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__


@dataclass
class Entry:
    seq: int
    method: str
    url: str
    request_headers: dict
    request_body: str | None = None
    status: int | None = None
    response_headers: dict = field(default_factory=dict)
    response_body: str | None = None
    elapsed_ms: float | None = None
    error: str | None = None


class Recorder:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.started_at = time.time()
        self.entries: list[Entry] = []
        self._seq = 0

    def begin(self, req: urllib.request.Request) -> Entry:
        self._seq += 1
        entry = Entry(
            seq=self._seq,
            method=req.get_method(),
            url=req.full_url,
            request_headers=dict(req.header_items()),
            request_body=req.data.decode() if req.data else None,
        )
        self.entries.append(entry)
        return entry

    def end(self, entry: Entry, *, status: int, headers: dict, body: str, elapsed_ms: float):
        entry.status = status
        entry.response_headers = headers
        entry.response_body = body[:4000]
        entry.elapsed_ms = round(elapsed_ms, 1)

    def fail(self, entry: Entry, error: str):
        entry.error = error

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "tool": "pplx-web",
            "version": __version__,
            "started_at": self.started_at,
            "entries": [
                {k: v for k, v in e.__dict__.items() if v is not None}
                for e in self.entries
            ],
        }

    def save(self, path: Path | None = None) -> Path:
        if path is None:
            path = Path(f"/tmp/pplx-web-trace-{self.trace_id[:8]}.json")
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path


def upload_trace(trace_path: Path, service_url: str) -> dict:
    data = trace_path.read_bytes()
    req = urllib.request.Request(
        service_url,
        data=data,
        method="POST",
        headers={
            "content-type": "application/json",
            "user-agent": f"pplx-web/{__version__}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())
