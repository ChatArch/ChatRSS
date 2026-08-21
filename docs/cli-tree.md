# ChatRSS CLI 树

这页按 ChatTea 文档风格展示命令面：先列可用 `chatrss --tree` / `chatrss --tree-brief` 回读的当前真实 CLI，再列 minor 版本目标树。目标树是设计约定，不等于当前 `--help` 已发布命令。

## 当前已实现命令树

以下完整命令树由 ChatStyle 从当前 Click 注册面生成，可用 `chatrss --tree` 直接回读：

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

`chatrss --tree-brief` 保留同一组节点和说明，但省略参数签名：

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

当前命令以“能跑通旧 watcher + 新 pipeline seam”为目标，没有把所有规划子命令提前做成空壳。

## Minor 目标命令树

```text
chatrss
├── config [规划]                            # 查看 ChatEnv-backed ChatRSS 配置摘要
│   ├── show                                 # 脱敏显示 active profile
│   └── doctor                               # 检查 RSSHub URL、ledger、action adapter 配置
├── trigger [规划]                           # 管理 trigger subscription
│   ├── list                                 # 列出 trigger jobs
│   ├── add                                  # 新增 RSS/RSSHub/webhook/API trigger job
│   ├── view                                 # 查看 trigger job、cursor、最近事件
│   ├── test                                 # 只拉取/标准化，不进入 action
│   ├── enable                               # 启用 trigger job
│   ├── disable                              # 禁用 trigger job
│   └── remove                               # 删除 trigger job；默认保留 ledger
├── event [规划]                             # 查看和回放标准化事件
│   ├── cat                                  # 按 source/connector/status 查看 event inbox
│   ├── view                                 # 查看单个 event envelope
│   ├── replay                               # 从 event 重新进入 router/action；默认 dry-run
│   └── import                               # 从 JSON/RSS fixture 导入事件做调试
├── router [规划]                            # 测试规则路由和模型路由
│   ├── test                                 # 用一个 event 文件输出 route decision
│   ├── explain                              # 展示规则命中、模型提示和决策原因
│   └── rules                                # 查看/校验 router rules 文件
├── model [规划]                             # 管理 model-router 配置和 dry-run 判断
│   ├── test                                 # 用固定事件检查模型决策 JSON schema
│   └── prompt                               # 打印/校验 model-router prompt 模板
├── action [规划]                            # 管理 action plan、审批和执行
│   ├── list                                 # 列出 action outbox
│   ├── view                                 # 查看 action job 和 idempotency key
│   ├── plan                                 # 只规划 action，不执行
│   ├── approve                              # 批准 draft/approval_required action
│   ├── run                                  # 执行已批准 action
│   └── adapters                             # 列出可用 action adapter
├── ledger [规划]                            # 查询事件、决策、动作和执行结果
│   ├── tail                                 # 追踪 JSONL/SQLite ledger
│   ├── query                                # 按 event_id/action_id/source 查询
│   └── doctor                               # 检查重复、失败、unknown result
├── connector [规划]                         # 检查 connector 能力和 fixture
│   ├── list                                 # 列出 rsshub/github/gitea/zulip 等 connector
│   └── test                                 # 单 connector 探测，输出 TriggerEvent
├── flow [部分已实现]                        # 端到端 pipeline 调试入口
│   ├── demo [已实现]                        # 内置示例事件 dry-run
│   └── run [规划]                           # 按 trigger job 跑一次完整 pipeline
├── server [已实现]                          # RSSHub local helper；不是 ChatRSS daemon
├── init [已实现]                            # 旧 watcher seen 初始化；后续并入 trigger add/test
├── watch [已实现]                           # 旧 RSSHub feed watcher；后续并入 trigger runner
├── cat [已实现]                             # 旧事件日志查看；后续并入 event/ledger
└── ps [已实现]                              # 旧 watch 进程检查
```

## 命令状态约定

| 状态 | 含义 |
| --- | --- |
| 已实现 | 当前 `chatrss --help` 或子命令 help 中真实存在，可测试。 |
| 部分已实现 | 命名空间已存在，但只覆盖一条 MVP 路径。 |
| 规划 | minor 版本目标，不应在 CLI 中返回成功占位。实现前只放在文档和设计中。 |

## 更新规则

1. 新增可执行命令时，先补可导入 Python API，再接 CLI。
2. 同步更新 `--help`、`docs/cli-tree.md`、`docs/interface-tree.md`、README 和 changelog。
3. 规划命令不能做成“打印计划后 exit 0”的 documentation-only command。
4. 外部写动作命令必须显式显示 dry-run / draft / approval / execute 边界。
