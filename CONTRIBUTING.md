# Contributing

## Bug reports

Good bug reports include reproduction steps and a trace. When triaging, try to reproduce the issue on a current sandbox image before commenting.

If the report involves connector behaviour, run the preflight with `--trace` to capture the full request/response exchange. The trace auto-uploads and returns a `trace_id` that can be shared in the issue thread.

```bash
pip install -e .
pplx-web preflight <connector> --trace
```

## Code changes

- Run `python -m pytest tests/ -v` before opening a PR
- Follow the existing code style
- Add tests for new features
