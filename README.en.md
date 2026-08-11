<div align="center">
    <a href="https://pypi.python.org/pypi/chatrss">
        <img src="https://img.shields.io/pypi/v/chatrss.svg" alt="PyPI version" />
    </a>
    <a href="./.github/workflows/ci.yml">
        <img src="https://img.shields.io/badge/ci-github_actions-blue.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatRSS/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# ChatRSS

ChatRSS is ChatArch's RSS / RSSHub-first trigger-router-action tool. RSSHub turns the outside world into feeds; ChatRSS turns feeds and other event sources into deduplicated, routed, auditable events that can trigger agents and controlled actions.

Documentation: <https://arch.gh.wzhecnu.cn/ChatRSS/>

## What works today

| Capability | Status | Entry point |
| --- | --- | --- |
| RSSHub/GitHub feed watching | Implemented | `chatrss watch` |
| Local RSSHub container helper | Implemented, requires local Docker / docker-compose | `chatrss server ...` |
| Local event log inspection | Implemented | `chatrss cat` |
| Trigger-Router-Action local flow | Implemented dry-run MVP | `chatrss flow demo` |
| Real Zulip / Discourse / Mattermost trigger + reply cases | Verified in a controlled service environment with shared actor `RexWang` | [Real-world cases](docs/real-world-cases.en.md) / [Mattermost](docs/platforms/mattermost.en.md) |
| Multi-platform trigger / router / action framework | Planned, with schema and dry-run seams already in place | [Capability map](docs/capability-map.en.md) |

## Quick start

```bash
python -m pip install -e ".[dev,docs]"
chatrss --help
chatrss --tree
chatrss --version
chatrss flow demo --ledger ./playground/flow.ledger.jsonl --json-output
python -m pytest -q
mkdocs build --strict
```

If `chatrss` is not installed globally, run from the source checkout:

```bash
PYTHONPATH=src python -m chatrss.cli flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

## Documentation map

- [Quick start](docs/quickstart.en.md): install, demo, watch, and RSSHub server boundary.
- [CLI tree](docs/cli-tree.en.md): `chatrss --tree` implemented command tree and minor-version target tree.
- [Capability map](docs/capability-map.en.md): Trigger, Event, Router, Model, Action, and Ledger status.
- [Interface tree](docs/interface-tree.en.md): CLI-to-Python API/module mapping.
- [Trigger-Router-Action design](docs/trigger-router-action.md): architecture and event protocol.
- [Real platform practice plan](docs/practice-plan.md): Zulip, Discourse, Mattermost, Revolt, GitHub, and Gitea sequence.
- [Real-world cases](docs/real-world-cases.en.md): verified Zulip, Discourse, and Mattermost actor -> watcher -> worker -> action-bot loops.
- [Zulip @mention quick start](docs/zulip-quickstart.en.md): Zulip trigger setup and verification.

## Minor-version direction

```text
Trigger Connector
  -> Event Schema / Inbox
  -> Rule Router
  -> Model Router
  -> Action Planner
  -> Action Executor
  -> Ledger
```

RSS / RSSHub are the first trigger connectors, not the entire workflow engine. External writes stay `dry-run`, `draft`, or `approval_required` until adapters, idempotency, and human approval are designed.

## Development notes

Read `DEVELOP.md`, `AGENTS.md`, and `docs/cli-tree.md` before expanding the package. New commands must update CLI help, tests, README, MkDocs pages, and the changelog together.
