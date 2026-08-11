# ChatRSS Quick Start

This page only covers commands that are executable today. Planned trigger/router/action subcommands are documented separately in the [CLI tree](cli-tree.en.md).

## Install and inspect

```bash
python -m pip install -e ".[dev,docs]"
chatrss --help
chatrss --tree
chatrss --version
```

Run from the source checkout without installing an entry point:

```bash
PYTHONPATH=src python -m chatrss.cli --help
```

## Run the local trigger-router-action flow

```bash
mkdir -p playground
chatrss flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

Expected result:

- `decision.decision` is `act`;
- actions include `internal.notify`, `agent.run`, and `github.comment`;
- the ledger contains `event_received`, `route_decision`, `action_planned`, and `action_result` records.

If the global entry point is unavailable:

```bash
PYTHONPATH=src python -m chatrss.cli flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

## Watch GitHub / RSSHub feeds

```bash
chatrss init ChatArch/ChatRSS --rsshub-url http://localhost:1200
chatrss watch ChatArch/ChatRSS --feeds issue,pull,comments --once --rsshub-url http://localhost:1200
```

`watch` is still the current GitHub/RSSHub feed watcher. It reads RSSHub routes, deduplicates seen items, and forwards task-like events to the existing notification/document actions. The new Event Schema and Router seam will gradually move this path into the unified pipeline.

## Local RSSHub server boundary

```bash
chatrss server start --port 1200
chatrss server status
chatrss server logs --tail 50
chatrss server stop
```

The `server` group depends on Docker / docker-compose. Machines without Docker must use an external RSSHub URL or public feeds; do not treat `server start` as a universal smoke test.

## Development verification

```bash
python -m pytest -q
mkdocs build --strict
python -m build
```
