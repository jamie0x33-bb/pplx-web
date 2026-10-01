# pplx-web

Browser automation helpers for Perplexity Computer. Drives connector-backed pages with Playwright, handles the authenticated preflight that resolves a connector's target URL before navigation.

## Install

```bash
pip install -e .
```

Playwright is optional — install `playwright` and run `playwright install chromium` for browser automation. The core preflight and diagnostics work without it.

## Usage

```bash
# Check connector availability and resolve target URL
pplx-web preflight gmail
pplx-web preflight google-drive --json

# Trace HTTP traffic for debugging
pplx-web preflight gmail --trace
# → saved to /tmp/pplx-web-trace-<id>.json

# Upload a trace for shared debugging
pplx-web trace upload /tmp/pplx-web-trace-*.json
# → returns a trace_id and viewer link

# Show runtime environment
pplx-web status
```

## Tracing

The `--trace` flag records all HTTP requests and responses made during the command. Trace files are JSON and can be uploaded to the project's trace viewer for collaborative debugging.

Traces include request headers. In a sandbox environment, this means the connector bearer is captured — upload only to trusted services.

## Development

```bash
python -m pytest tests/ -v
```

## License

MIT
