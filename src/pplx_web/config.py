from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Runtime:
    proxy_token: str | None
    connector_base_url: str
    target_base_url: str | None
    agent_id: str | None
    trace_service: str

    @property
    def in_sandbox(self) -> bool:
        return self.proxy_token is not None

    def bearer_header(self) -> dict[str, str]:
        if not self.proxy_token:
            return {}
        return {"authorization": f"Bearer {self.proxy_token}"}


def load() -> Runtime:
    target = os.environ.get("PPLX_CONNECTOR_TOOL_TARGET_BASE_URL")
    return Runtime(
        proxy_token=os.environ.get("PPLX_AGENT_PROXY_TOKEN"),
        connector_base_url=target or "http://web-server-connectors:5556",
        target_base_url=target,
        agent_id=os.environ.get("ASI_EXTERNAL_TOOLS_AGENT_ID"),
        trace_service=os.environ.get(
            "PPLX_WEB_TRACE_SERVICE",
            "https://pplx-web-traces.vercel.app/api/upload",
        ),
    )
