# ChatRSS CLI Tree

This page follows the ChatTea documentation pattern: show the real command surface first, then the minor-version target tree. The target tree is a design contract, not current `--help` output.

## Implemented command tree

```text
chatrss                                      # RSSHub feed watcher + event-routing experiment entry
├── init [implemented]                       # Initialize seen state to avoid replaying historical items
├── watch [implemented]                      # Watch GitHub/RSSHub feeds and notify/write docs for new items
├── cat [implemented]                        # Read local event logs without network access
├── ps [implemented]                         # Show currently running chatrss watch processes
├── server [implemented]                     # Manage local RSSHub service; requires Docker/docker-compose
│   ├── start                                # Start RSSHub container
│   ├── stop                                 # Stop RSSHub container
│   ├── restart                              # Restart RSSHub container
│   ├── status                               # Show container status and health
│   ├── logs                                 # Show container logs
│   └── url                                  # Print current RSSHub URL
└── flow [implemented]                       # Run local trigger-router-action flow
    └── demo                                 # Built-in demo event -> router -> dry-run actions -> ledger
```

The current CLI intentionally runs the old watcher and the new pipeline seam. Planned subcommands are not exposed as successful placeholders.

## Minor-version target tree

```text
chatrss
├── config [planned]                         # Inspect ChatEnv-backed ChatRSS configuration
│   ├── show                                 # Show redacted active profile
│   └── doctor                               # Check RSSHub URL, ledger, and action adapter config
├── trigger [planned]                        # Manage trigger subscriptions
│   ├── list                                 # List trigger jobs
│   ├── add                                  # Add RSS/RSSHub/webhook/API trigger job
│   ├── view                                 # Show trigger job, cursor, and recent events
│   ├── test                                 # Fetch/normalize only; do not enter actions
│   ├── enable                               # Enable trigger job
│   ├── disable                              # Disable trigger job
│   └── remove                               # Remove trigger job; keep ledger by default
├── event [planned]                          # Inspect and replay normalized events
│   ├── cat                                  # List event inbox by source/connector/status
│   ├── view                                 # Show one event envelope
│   ├── replay                               # Re-enter router/action from an event; dry-run by default
│   └── import                               # Import JSON/RSS fixtures for debugging
├── router [planned]                         # Test rule-router and model-router behavior
│   ├── test                                 # Output route decision for one event file
│   ├── explain                              # Show rule match, model prompt, and decision reason
│   └── rules                                # View/validate router rules file
├── model [planned]                          # Manage model-router configuration and dry-run decisions
│   ├── test                                 # Check model decision JSON schema with a fixed event
│   └── prompt                               # Print/validate model-router prompt template
├── action [planned]                         # Manage action plan, approval, and execution
│   ├── list                                 # List action outbox
│   ├── view                                 # Show action job and idempotency key
│   ├── plan                                 # Plan actions only
│   ├── approve                              # Approve draft/approval_required actions
│   ├── run                                  # Execute approved actions
│   └── adapters                             # List available action adapters
├── ledger [planned]                         # Query events, decisions, actions, and results
│   ├── tail                                 # Follow JSONL/SQLite ledger
│   ├── query                                # Query by event_id/action_id/source
│   └── doctor                               # Check duplicates, failures, and unknown results
├── connector [planned]                      # Inspect connector capabilities and fixtures
│   ├── list                                 # List rsshub/github/gitea/zulip connectors
│   └── test                                 # Probe one connector and output TriggerEvent
├── flow [partly implemented]                # End-to-end pipeline debugging
│   ├── demo [implemented]                   # Built-in demo event dry-run
│   └── run [planned]                        # Run one full pipeline from trigger job
├── server [implemented]                     # RSSHub local helper; not a ChatRSS daemon
├── init [implemented]                       # Legacy watcher seen initialization
├── watch [implemented]                      # Legacy RSSHub feed watcher
├── cat [implemented]                        # Legacy event log reader
└── ps [implemented]                         # Legacy watch process inspection
```

## Status contract

| Status | Meaning |
| --- | --- |
| implemented | Exists in current `chatrss --help` or subcommand help and is testable. |
| partly implemented | Namespace exists, but only one MVP path is available. |
| planned | Minor-version target. It must not be represented by a successful placeholder command. |

## Update rules

1. Add an importable Python API before wiring a new executable command.
2. Update `--help`, `docs/cli-tree.md`, `docs/interface-tree.md`, README, and changelog together.
3. Do not add documentation-only commands that print plans and exit successfully.
4. External-write commands must expose dry-run, draft, approval, and execute boundaries clearly.
