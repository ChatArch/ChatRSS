# Trigger-Router-Action 初步设计

ChatRSS 的 minor 版本方向不再只是“GitHub RSS 通知器”，而是一个以 RSS/RSSHub 为第一批 trigger connector 的 Agent 事件路由系统。

## 核心抽象

```text
Trigger -> Event Schema -> Router -> Action Planner -> Action Executor -> Ledger
```

对应用户给出的产品抽象：

```text
(trigger, router, action)
```

## 1. Trigger：只负责发现和标准化事件

Trigger 层可以来自：

- RSS feed
- RSSHub route
- Webhook
- API poller
- 后续的 Feishu/Discord/GitHub native event connector

MVP 先只落 RSS/RSSHub。Trigger 不直接发送消息、不直接评论、不直接启动 agent。它只把外部 item 转成统一事件，并交给后续层。

## 2. Event Schema：连接层协议

后续 Router 和 Action 不应关心事件最初来自 RSSHub 还是 webhook。统一事件结构如下：

```json
{
  "event_id": "rsshub:comments:abc123",
  "source": "rsshub",
  "connector": "comments",
  "event_type": "github.comment.item",
  "title": "New comment on issue #12",
  "url": "https://github.com/ChatArch/ChatRSS/issues/12#issuecomment-456",
  "content": "请帮忙更新文档",
  "published_at": "2026-08-05T10:00:00Z",
  "actor": {
    "type": "github_user",
    "id": "some-user",
    "display_name": "some-user"
  },
  "subject": {
    "type": "github.issue",
    "repo": "ChatArch/ChatRSS",
    "number": "12"
  },
  "raw": {}
}
```

## 3. Router：规则先过滤，模型再判断

Router 分两段：

1. **Rule Router**：便宜、确定、快速。按 `connector`、`actor`、`repo`、`event_type`、关键词等做第一层过滤。
2. **Model Router**：只处理通过规则的事件，判断是否需要 action、需要什么上下文、风险等级和是否需要人工确认。

MVP 的规则：

| connector | 默认处理 |
| --- | --- |
| `issue` | 进入 model router |
| `pull` | 进入 model router |
| `comments` | 进入 model router |
| `repo_event` | 只归档 |

MVP 的 model router 先用 deterministic heuristic stub 模拟：如果标题或正文里出现“请、帮、更新、修复、review、回复、留言、agent、任务”等词，就规划 agent action；评论类事件额外规划一个 draft comment action。

## 4. Action Planner / Executor

Model Router 输出的是“应该做什么”，不直接执行外部副作用。

Action Planner 把决策转成 action job：

```json
{
  "action_id": "act_...",
  "event_id": "evt_...",
  "type": "agent.run",
  "mode": "dry_run",
  "idempotency_key": "agent.run:evt_...:v1",
  "requires_approval": false,
  "input": {
    "task": "Read the linked thread and prepare a response."
  }
}
```

Executor MVP 只做 dry-run，写入 ledger，不真实发评论或启动外部 agent。后续可替换为 adapter：

- `feishu.message`
- `feishu.doc.append`
- `github.comment`
- `agent.run`
- `webhook.call`

高风险外部动作默认应该 draft / approval required。

## 5. Ledger：把完整因果链落盘

MVP 用 JSONL ledger，记录：

- `event_received`
- `route_decision`
- `action_planned`
- `action_result`

后续可以把 JSONL 换成 SQLite/Postgres，但接口上先保持 durable ledger 概念。

## 6. 实践来源

这套抽象需要尽快绑定真实、可实践的 trigger 来源。优先来源分两类：

### 社区对话来源

`zhihong.oray` 上已有 Discourse、Zulip、Revolt 等社区/对话服务，可以作为 ChatRSS 触发器的实践环境。第一阶段不急着做全平台 adapter，而是定义每个平台最小信号：

| 平台 | 第一信号 | Trigger 目标 |
| --- | --- | --- |
| Discourse | 新帖、回复、@mention、指定用户发言 | 产生 `community.post.created` / `community.mention.created` 事件 |
| Zulip | 指定 stream/topic 中的新消息、@mention、指定 sender | 产生 `community.message.created` 事件 |
| Revolt | 指定 channel 中的新消息、@mention、指定 sender | 产生 `community.message.created` 事件 |

实践验收样例：一个模型或用户在社区中发帖/留言并 @ 某个约定对象；ChatRSS connector 能收到信号，标准化成 Event，Router 判断后生成提醒或 agent dry-run action。

### 项目进展来源

GitHub 项目仍然是最容易先跑通的来源：

| 来源 | Trigger |
| --- | --- |
| GitHub issue | RSSHub `/github/issue/:user/:repo/:state?/:labels?` |
| GitHub PR | RSSHub `/github/pull/:user/:repo/:state?/:labels?` |
| GitHub comments | RSSHub `/github/comments/:user/:repo/:number?` |
| GitHub repo events | RSSHub `/github/repo_event/:owner/:repo/:types?` |

实践验收样例：关注一个已有 GitHub 项目；出现 issue/PR/comment 更新时，ChatRSS 收到 feed item，生成标准 Event，并输出 action 提醒信号。

## 7. MVP 验收流

本轮先跑通：

```text
sample RSSHub comment event
  -> TriggerEvent schema
  -> Rule Router 命中 comments -> model_router
  -> Model Router 判断需要 act
  -> Action Planner 生成 agent.run + github.comment draft
  -> Dry-run Executor 写 action_result
  -> JSONL Ledger 可回读
```

CLI：

```bash
chatrss flow demo --ledger ./playground/ledger.jsonl --json-output
```

验收：命令输出 decision 为 `act`，actions 包含 `agent.run` 与 `github.comment`，ledger 至少写入 event、decision、action result。
