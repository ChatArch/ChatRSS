# ChatRSS 接口树

接口树用于把 CLI 命令、Python 模块和可复用函数对齐。CLI 只做参数解析和输出，核心能力应在可导入 Python API 中实现。

## 当前 CLI 到 Python 的映射

```text
chatrss
├── --tree / --tree-brief
│   └── chatstyle.add_tree_option() → chatrss.cli.main 注册面
├── init
│   └── chatrss.watcher.init_seen(repo, rsshub_url)
├── watch
│   ├── chatrss.watcher.poll_once(repo, rsshub_url, feeds)
│   └── chatrss.actions.process_items(...)
├── cat
│   └── chatrss.actions / 本地事件日志读取
├── ps
│   └── chatrss.cli 进程检查 helper
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

## 新架构模块

| 模块 | 责任 |
| --- | --- |
| `chatrss.events` | `TriggerEvent`、`EventSubject`、`EventActor`、`RouteDecision`、`ActionJob`、`ActionResult` schema。 |
| `chatrss.pipeline` | event 标准化、规则路由、model-router stub、action planning、dry-run execution、JSONL ledger。 |
| `chatrss.feed` | RSS/RSSHub feed 解析和 `FeedItem`。 |
| `chatrss.watcher` | 旧 GitHub/RSSHub watcher：poll、seen state、feed orchestration。 |
| `chatrss.actions` | 旧通知/飞书文档/本地事件日志 action 逻辑。 |
| `chatrss.server` | 本地 RSSHub Docker/docker-compose helper。 |
| `chatrss.config` | ChatEnv-backed 配置定义。 |

## 目标接口分层

```text
connector.*      # RSSHub / GitHub / Gitea / Zulip / Discourse / Revolt 事件采集
normalizer.*     # source-specific raw payload -> TriggerEvent
inbox.*          # durable event inbox / cursor / dedupe
router.*         # rule router + model router
planner.*        # RouteDecision -> ActionJob
executor.*       # ActionJob -> ActionResult；真实 adapter 放这里
ledger.*         # audit/replay/query/failure state
```

规划接口必须先有真实行为和测试，再暴露 CLI 命令；不要为文档蓝图添加空命令。
