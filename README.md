# renovate-burndown-demo

Order-service sandbox with intentionally outdated Python, Node, Docker and GitHub Actions
dependencies. Renovate opens the update PRs; Devin validates each one in parallel.

- Python: `python -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python -m pytest tests -q`
- Node: `npm install && npm test`
