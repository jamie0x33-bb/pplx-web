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

# Show runtime environment
pplx-web status
```

## Development

```bash
python -m pytest tests/ -v
```

## License

MIT
