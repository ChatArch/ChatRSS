# ChatRSS 文档

ChatRSS 是 RSS / RSSHub-first 的 Agent 触发器：它把 feed、通知、社区消息和代码托管事件标准化为 Event，再交给 Router、Model、Action 和 Ledger 处理。

站点入口：<https://arch.gh.wzhecnu.cn/ChatRSS/>

## 按场景选择文档

| 场景 | 文档 |
| --- | --- |
| 我想快速跑通本地闭环 | [快速开始](quickstart.md) |
| 我想看当前命令和 minor 目标命令 | [CLI 树](cli-tree.md) |
| 我想确认 ChatRSS 到底负责哪些能力 | [能力地图](capability-map.md) |
| 我想把 CLI 和 Python API 对上 | [接口树](interface-tree.md) |
| 我想理解 Trigger / Schema / Router / Model / Action / Ledger 抽象 | [Trigger-Router-Action 设计](trigger-router-action.md) |
| 我想选真实平台做 trigger 实践 | [真实平台实践计划](practice-plan.md) |
| 我想复查真实平台链路 | [真实事件案例](real-world-cases.md) / [Zulip @mention 快速开始](zulip-quickstart.md) |

## 文档栏目组织

<div class="grid cards" markdown>

- **入门**

  本地安装、`flow demo`、RSSHub feed watch 和 RSSHub server 边界。

- **命令与接口**

  用 ChatTea 风格展示当前 CLI 树、预计 minor CLI 树、能力地图和 Python 接口映射。

- **架构**

  固化 `Trigger -> Event Schema -> Router -> Model -> Action -> Ledger` 的长期抽象。

- **实践**

  以 Zulip 为已验证真实 trigger 和回帖案例，后续扩展到 Discourse、Revolt、GitHub 和 Gitea。

</div>

## 当前安全默认值

- Trigger 只发现和标准化事件，不直接执行外部动作。
- `repo_event` 默认作为背景上下文归档，避免噪音。
- 外部写动作默认 `dry_run`、`draft` 或 `approval_required`。
- Ledger 记录事件、决策、动作和结果，不记录 token / password / API key。

## 本地预览

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```
