# renovate-burndown-demo

Order-service sandbox with intentionally outdated Python, Node, Docker and GitHub Actions
dependencies. Renovate opens the update PRs; Devin validates each one in parallel.

Prerequisites: Python 3.9 to 3.11 (CI uses 3.9) and Node 16 or newer (CI uses 16). On Python 3.12.4
and newer (tested on 3.12 and 3.13), `tests/test_orders.py::test_fastapi_health` fails with `TypeError: ForwardRef._evaluate()`
because the pinned pydantic 1.10.13 predates support for them.

- Python: `python3.9 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python -m pytest tests -q`
- Node: `npm install && npm test`
