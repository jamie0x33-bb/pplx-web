from pplx_web.config import load


def test_load_outside_sandbox(monkeypatch):
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    rt = load()
    assert not rt.in_sandbox
    assert rt.bearer_header() == {}


def test_load_in_sandbox(monkeypatch):
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "test-token")
    monkeypatch.setenv("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL", "http://connectors:5556")
    rt = load()
    assert rt.in_sandbox
    assert rt.bearer_header() == {"authorization": "Bearer test-token"}
    assert rt.connector_base_url == "http://connectors:5556"
