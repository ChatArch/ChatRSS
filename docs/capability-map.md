# ChatRSS 能力地图

能力地图回答“ChatRSS 负责什么、不负责什么”。命令调用方式见 [CLI 树](cli-tree.md)，Python 映射见 [接口树](interface-tree.md)。

## 当前能力面

| 能力 | 当前状态 | 当前入口 | Minor 目标 |
| --- | --- | --- | --- |
| RSSHub/GitHub feed connector | 已实现旧 watcher 路径 | `chatrss init` / `chatrss watch` | 纳入 `trigger add/test/run` |
| Event Schema | 已实现 `TriggerEvent` / `ActionJob` / `RouteDecision` | `chatrss.events` | 所有 connector 统一输出这个 envelope |
| Rule Router | 已实现最小规则 | `chatrss.pipeline.route_event` | 可配置 YAML/JSON rules，先降噪再进模型 |
| Model Router | 已实现 deterministic stub | `chatrss.pipeline.model_route_event` | LLM JSON decision，保留 schema 校验和解释 |
| Action Planner | 已实现 dry-run plan；真实平台案例已记录 `zulip.message.reply` 和 `discourse.post.reply` action | `chatrss.pipeline.plan_actions` / [真实事件案例](real-world-cases.md) | 输出 action outbox，带 idempotency key |
| Action Executor | 包内已实现 dry-run executor；远端实践验证 Zulip 与 Discourse action bot 回帖 | `chatrss.pipeline.execute_action` / [真实事件案例](real-world-cases.md) | Feishu/GitHub/Gitea/Zulip/agent adapters |
| Ledger | 已实现 JSONL flow ledger | `chatrss.pipeline.append_ledger` / `read_ledger` | SQLite/Postgres inbox/outbox/ledger，可重放和审计 |
| 真实社区 trigger | 已验证 Zulip @mention 与 Discourse topic/post -> worker -> action bot 回帖 | [真实事件案例](real-world-cases.md) / [Zulip quick start](zulip-quickstart.md) | Zulip/Discourse/Revolt connector |

## 责任边界

<div class="grid cards" markdown>

- **Trigger Connector**

  读取 RSS、RSSHub、webhook、notification API 或社区消息 API，只输出标准 Event。

- **Router / Model**

  规则先过滤噪音，模型再判断意图、优先级、上下文需求和动作类型。

- **Action / Ledger**

  Action Planner 只生成 job；Executor 通过 adapter 执行；Ledger 保证审计、幂等、失败恢复。

</div>

## 明确不做

- 不把 RSSHub 变成 workflow engine；RSSHub 是 trigger stream provider。
- 不让 trigger connector 直接发消息、评论、merge、发布或改配置。
- 不把规划命令做成返回成功的 CLI 空壳。
- 不在 ledger、报告、README 或文档中保存 token、password、API key。
- 不默认执行真实外部写动作；写动作必须 dry-run/draft/approval 分层，只有明确授权的案例才执行并验证。

## 平台扩展优先级

| 来源 | 优先入口 | 第一动作 |
| --- | --- | --- |
| GitHub 项目进展 | RSSHub routes / comments / issue / PR | notify + agent.run + comment draft |
| Gitea 协作事件 | notifications API / issue / PR comments | agent.run + gitea.comment.draft |
| Zulip 社区消息 | messages/events API + mention flag | agent.run + zulip.message.reply（默认 draft/approval，可授权执行） |
| Discourse 论坛 | notifications/topics/posts API / posts watcher | agent.run + discourse.post.reply（默认 draft/approval，可授权执行） |
| Revolt 频道 | bot token + gateway 或 REST polling | agent.run + revolt.message.draft |
