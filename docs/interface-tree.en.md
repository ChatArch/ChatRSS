# ChatRSS Interface Tree

The interface tree maps CLI commands to Python modules and reusable functions. The CLI should parse arguments and render output; core behavior should live in importable Python APIs.

## Current CLI-to-Python mapping

```text
chatrss
├── init
│   └── chatrss.watcher.init_seen(repo, rsshub_url)
├── watch
│   ├── chatrss.watcher.poll_once(repo, rsshub_url, feeds)
│   └── chatrss.actions.process_items(...)
├── cat
│   └── chatrss.actions / local event-log reader
├── ps
│   └── chatrss.cli process-inspection helper
├── server
│   ├── chatrss.server.start(port)
│   ├── chatrss.server.stop()
│   ├── chatrss.server.restart()
│   ├── chatrss.server.status()
│   ├── chatrss.server.logs(tail)
│   ├── chatrss.server.get_url(port)
│   └── chatrss.server.is_running(port)
└── flow
    └── demo
        ├── chatrss.pipeline.sample_multi_agent_event()
        ├── chatrss.pipeline.run_event_flow(event, ledger_path)
        └── chatrss.pipeline.read_ledger(path)
```

## New architecture modules

| Module | Responsibility |
| --- | --- |
| `chatrss.events` | `TriggerEvent`, `EventSubject`, `EventActor`, `RouteDecision`, `ActionJob`, and `ActionResult` schemas. |
| `chatrss.pipeline` | Event normalization, rule routing, model-router stub, action planning, dry-run execution, and JSONL ledger. |
| `chatrss.feed` | RSS/RSSHub feed parsing and `FeedItem`. |
| `chatrss.watcher` | Legacy GitHub/RSSHub watcher: poll, seen state, and feed orchestration. |
| `chatrss.actions` | Legacy notification, Feishu doc, and local event-log action logic. |
| `chatrss.server` | Local RSSHub Docker/docker-compose helper. |
| `chatrss.config` | ChatEnv-backed configuration definition. |

## Target interface layering

```text
connector.*      # RSSHub / GitHub / Gitea / Zulip / Discourse / Revolt collection
normalizer.*     # source-specific raw payload -> TriggerEvent
inbox.*          # durable event inbox / cursor / dedupe
router.*         # rule router + model router
planner.*        # RouteDecision -> ActionJob
executor.*       # ActionJob -> ActionResult; real adapters live here
ledger.*         # audit/replay/query/failure state
```

Planned interfaces must have real behavior and tests before becoming CLI commands. Do not add empty commands for documentation blueprints.
