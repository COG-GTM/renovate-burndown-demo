# renovate-burndown-demo

Order-service sandbox with intentionally outdated Python, Node, Docker and GitHub Actions
dependencies. Renovate opens the update PRs; Devin validates each one in parallel.

See [docs/architecture.md](docs/architecture.md) for how the pieces fit together, with a
diagram.

## Layout

| Path | Contents |
| --- | --- |
| `app/` | Python order service (FastAPI + pydantic v1): `main.py`, `orders.py`, `config.py` |
| `src/server.js` | Node order service (Express + zod) |
| `tests/` | pytest suite for the Python service |
| `test/smoke.test.js` | Node smoke test |
| `Dockerfile` | Image for the Python service (`python:3.9-slim`, port 8000) |
| `.github/workflows/ci.yml` | CI: Python 3.9 pytest job and Node 16 `npm test` job |
| `renovate.json` | Renovate config: grouped non-major PR, separate majors, security alerts |
| `docs/` | Architecture doc and Graphviz diagram (`docs/diagrams/`) |

## Setup

CI uses Python 3.9 and Node 16; match those locally, since the pinned dependencies are old.

### Python service

```bash
python3.9 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests -q
```

`requirements.txt` does not include an ASGI server. To run the API locally, install one
into the venv, then start it:

```bash
.venv/bin/pip install uvicorn
.venv/bin/uvicorn app.main:app --port 8000
curl localhost:8000/health
```

Interactive API docs are at `http://localhost:8000/docs`. Settings come from `ORDERS_*`
environment variables (for example `ORDERS_MAX_ORDER_ITEMS=10`); see
[docs/architecture.md](docs/architecture.md#python-service-app).

### Node service

```bash
npm install
npm test
npm start            # listens on $PORT, default 3000
curl localhost:3000/health
```

### Container

```bash
docker build -t renovate-burndown-demo .
```

The image's `CMD` runs `uvicorn`, which is not in `requirements.txt`, so the container
exits at start on `main`.

## Diagram

Edit `docs/diagrams/architecture.dot` and run `docs/diagrams/render.sh` (needs Graphviz) to
regenerate `architecture.png` and `architecture.svg`.
