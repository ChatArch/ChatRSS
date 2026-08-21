# ChatRSS CLI Tree

This page follows the ChatTea documentation pattern: show the current real CLI that can be read back with `chatrss --tree` / `chatrss --tree-brief`, then the minor-version target tree. The target tree is a design contract, not current `--help` output.

## Implemented command tree

ChatStyle generates this full tree from the currently registered Click surface; read it back with `chatrss --tree`:

```text
chatrss
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── cat [REPO] [--limit LIMIT] [--json-output]  # 只读输出本地事件日志；不访问网络。
├── flow  # 运行 trigger-router-action 本地 dry-run 闭环。
│   └── demo [--ledger LEDGER] [--json-output]  # 用内置事件 dry-run action 并写 JSONL ledger。
├── init [REPO] [--rsshub-url RSSHUB-URL]  # 拉取 feed 并写 seen 状态，避免首次运行重放历史条目。
├── ps  # 只读输出当前 chatrss watch 进程。
├── server  # 管理本地 RSSHub Docker 服务；可能变更容器状态。
│   ├── logs [--tail TAIL]  # 只读输出 RSSHub 容器日志。
│   ├── restart  # 重启 RSSHub 容器；写 Docker 状态。
│   ├── start [--port PORT]  # 启动 RSSHub 容器并输出服务 URL；写 Docker 状态。
│   ├── status  # 只读查看 RSSHub 容器状态和健康检查。
│   ├── stop  # 停止 RSSHub 容器；写 Docker 状态。
│   └── url  # 只读输出当前 RSSHub 地址和运行状态。
└── watch [REPO] [--interval INTERVAL] [--rsshub-url RSSHUB-URL] [--feeds FEEDS] [--doc DOC] [--notify-user NOTIFY-USER] [--once]  # 轮询 feed、写事件日志，并可通知飞书和更新文档。
```

`chatrss --tree-brief` preserves the same nodes and summaries while omitting parameter signatures:

```text
chatrss
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
├── cat  # 只读输出本地事件日志；不访问网络。
├── flow  # 运行 trigger-router-action 本地 dry-run 闭环。
│   └── demo  # 用内置事件 dry-run action 并写 JSONL ledger。
├── init  # 拉取 feed 并写 seen 状态，避免首次运行重放历史条目。
├── ps  # 只读输出当前 chatrss watch 进程。
├── server  # 管理本地 RSSHub Docker 服务；可能变更容器状态。
│   ├── logs  # 只读输出 RSSHub 容器日志。
│   ├── restart  # 重启 RSSHub 容器；写 Docker 状态。
│   ├── start  # 启动 RSSHub 容器并输出服务 URL；写 Docker 状态。
│   ├── status  # 只读查看 RSSHub 容器状态和健康检查。
│   ├── stop  # 停止 RSSHub 容器；写 Docker 状态。
│   └── url  # 只读输出当前 RSSHub 地址和运行状态。
└── watch  # 轮询 feed、写事件日志，并可通知飞书和更新文档。
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
