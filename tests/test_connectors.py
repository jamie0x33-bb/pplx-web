import json
from unittest.mock import patch, MagicMock

import pytest

from pplx_web.config import load
from pplx_web.connectors import preflight, list_connectors, ConnectorError
from pplx_web.trace import Recorder


def _mock_response(body: dict, status: int = 200):
    mock = MagicMock()
    mock.status = status
    mock.read.return_value = json.dumps(body).encode()
    mock.headers = {"content-type": "application/json"}
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_preflight_sends_bearer(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "test-bearer")
    monkeypatch.setenv("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL", "http://connectors:5556")
    rt = load()

    resp = _mock_response({"status": "connected", "target_base_url": "https://gmail.googleapis.com"})

    with patch("urllib.request.urlopen", return_value=resp) as mock_open:
        result = preflight(rt, "gmail")

    req = mock_open.call_args[0][0]
    assert req.get_header("Authorization") == "Bearer test-bearer"
    assert result["status"] == "connected"


def test_preflight_with_trace(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "test-bearer")
    rt = load()
    recorder = Recorder()

    resp = _mock_response({"status": "connected"})

    with patch("urllib.request.urlopen", return_value=resp):
        preflight(rt, "gmail", recorder=recorder)

    assert len(recorder.entries) == 1
    assert recorder.entries[0].status == 200


def test_preflight_error(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "test-bearer")
    rt = load()

    import urllib.error
    err = urllib.error.HTTPError("http://x", 401, "Unauthorized", {}, None)

    with patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(ConnectorError) as exc_info:
            preflight(rt, "gmail")
    assert exc_info.value.status == 401


def test_list_connectors(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "test-bearer")
    rt = load()

    resp = _mock_response({"connectors": [{"name": "gmail"}, {"name": "google-drive"}]})

    with patch("urllib.request.urlopen", return_value=resp):
        items = list_connectors(rt)

    assert len(items) == 2
    assert items[0]["name"] == "gmail"
