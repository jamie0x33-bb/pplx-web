import json
import urllib.request
from pathlib import Path
from unittest.mock import patch, MagicMock

from pplx_web.trace import Recorder, upload_trace


def test_recorder_captures_request():
    rec = Recorder()
    req = urllib.request.Request(
        "http://example.com/api",
        data=b'{"test": true}',
        method="POST",
        headers={"Authorization": "Bearer tok", "Content-Type": "application/json"},
    )
    entry = rec.begin(req)
    rec.end(entry, status=200, headers={"x-req-id": "abc"}, body='{"ok": true}', elapsed_ms=42.5)

    assert len(rec.entries) == 1
    assert entry.status == 200
    assert entry.elapsed_ms == 42.5


def test_recorder_save(tmp_path):
    rec = Recorder()
    req = urllib.request.Request("http://example.com/test", method="GET")
    entry = rec.begin(req)
    rec.end(entry, status=200, headers={}, body="", elapsed_ms=1.0)

    path = rec.save(tmp_path / "trace.json")
    assert path.exists()

    data = json.loads(path.read_text())
    assert data["tool"] == "pplx-web"
    assert len(data["entries"]) == 1


def test_recorder_fail():
    rec = Recorder()
    req = urllib.request.Request("http://example.com/fail", method="GET")
    entry = rec.begin(req)
    rec.fail(entry, "connection refused")
    assert entry.error == "connection refused"
    assert entry.status is None


def test_upload_trace(tmp_path):
    trace_file = tmp_path / "trace.json"
    trace_file.write_text(json.dumps({"trace_id": "test-id", "entries": []}))

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(
        {"accepted": True, "trace_id": "test-id", "viewer_url": "https://example.com/view/test-id"}
    ).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = upload_trace(trace_file, "https://example.com/api/upload")

    assert result["accepted"] is True
    assert result["trace_id"] == "test-id"
