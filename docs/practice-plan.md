# ChatRSS 真实平台实践计划

目标：用现有社区和代码托管平台跑通真实 trigger，而不是只停留在抽象 demo。第一批实践来源包括 受控服务环境 上的 Zulip、Discourse、Mattermost、Revolt，以及 GitHub/Gitea 项目进展。

## 已验证平台入口

| 平台 | 独立文档 | 统一 actor | 接入判断 |
| --- | --- | --- | --- |
| Zulip | [Zulip 平台案例](platforms/zulip.md) | `RexWang` | 直接用 Zulip messages/events API；不需要 RSSHub。 |
| Discourse | [Discourse 平台案例](platforms/discourse.md) | `RexWang` | 适合 forum/topic connector；登录态/API/服务端回读验收。 |
| Mattermost | [Mattermost 平台案例](platforms/mattermost.md) | `RexWang` | 实时 Agent 房间优先走 Hermes/Mattermost gateway；ChatRSS 只在需要统一去重、路由和 ledger 时接入。 |

这些平台的共同产品语义是：

```text
前置动作 / platform event / feed item
  -> Trigger Connector
  -> TriggerEvent
  -> Event Inbox / Dedupe
  -> Rule Router
  -> Model Router
  -> Action Planner
  -> Action Executor
  -> Ledger / Audit
```

## 1. 实践原则

1. **Trigger 用托管账号轮询/接收事件**：每个平台准备一个由 ChatRSS 托管的 watcher/bot 账号，用 API token / bot token / webhook secret 读取它能看到的信息。
2. **平台机制优先**：优先使用官方 API、bot API、webhook、notification API；RSS/RSSHub 作为项目进展和公开内容的第一入口，也可作为没有 webhook 时的 fallback。
3. **账号隔离**：至少区分：
   - `actor account`：用于发帖、评论、@mention，模拟真实用户或模型。
   - `watcher account`：由 ChatRSS 托管，专门接收 mention/通知/消息。
   - `action account`：需要真实回复/留言时才启用；默认 dry-run/draft，明确授权后可执行并验证。
4. **Trigger 不直接执行动作**：trigger 捕获信号后只产出标准 Event，后续由 router/model/action 处理。
5. **外部写动作默认 dry-run / draft**：真实回复、发帖、评论必须进入审批或单独授权；已验证 Zulip 和 Discourse 授权回帖案例见 [真实事件案例](real-world-cases.md)。

## 2. 平台和第一批 trigger 定义

### 2.1 Discourse

实践对象：论坛帖、回复、@mention。

建议账号：

| 账号 | 用途 |
| --- | --- |
| `discourse-actor` | 发帖、回复、@ watcher。 |
| `discourse-watcher` | ChatRSS 托管，读取 notifications / topics / posts。 |
| `discourse-action` | 后续真实回复账号；默认 draft/approval，授权案例中执行 `discourse.post.reply`。 |

优先入口：

- Discourse API key + username；
- notifications endpoint，用 watcher 账号检查 @mention / reply；
- topics/posts endpoint，用于读取关联上下文。

已验证实践：`RexWang` 在 `Agent Runs` 分类创建真实 topic/post，`discourse.posts` watcher 标准化为 `discourse:post:25:mention:system`，action executor 写入 `discourse.post.reply`，并用 RexWang 登录态回读 topic JSON 验证 post `25` 与 reply `26`。详见 [真实事件案例](real-world-cases.md)。

第一批规则：

```yaml
- name: discourse-mention-to-agent
  source: discourse
  connector: discourse.notifications
  when:
    notification_type: mention
    account: discourse-watcher
  context:
    read_topic: true
    max_posts: 20
  actions:
    - agent.run
    - discourse.reply.draft
```

标准事件示例：

```json
{
  "source": "discourse",
  "connector": "discourse.notifications",
  "event_type": "community.mention.created",
  "actor": {"type": "discourse_user", "id": "discourse-actor"},
  "subject": {"type": "discourse.topic", "number": "123"},
  "url": "https://.../t/topic/123/4",
  "content": "@discourse-watcher 请总结这个帖子并给出建议"
}
```

### 2.2 Zulip

实践对象：stream/topic 消息、@mention、私信。

建议账号：

| 账号 | 用途 |
| --- | --- |
| `zulip-actor` | 在指定 stream/topic 发消息或 @ watcher。 |
| `zulip-watcher-bot` | ChatRSS 托管 bot，轮询 events 或 messages。 |
| `zulip-action-bot` | 真实回复 bot；默认 dry-run/draft，授权案例中执行 `zulip.message.reply`。 |

优先入口：

- Zulip bot email + API key；
- events/register + events 队列，或 messages endpoint 轮询；
- narrow 到指定 stream/topic/mention。

第一批规则：

```yaml
- name: zulip-mention-to-agent
  source: zulip
  connector: zulip.messages
  when:
    mentioned: true
    account: zulip-watcher-bot
    stream: multi-agent
  context:
    read_topic: true
    max_messages: 50
  actions:
    - agent.run
    - zulip.message.draft  # default
    - zulip.message.reply   # authorized case only
```

### 2.3 Revolt

实践对象：channel 消息、mention、指定用户消息。

建议账号：

| 账号 | 用途 |
| --- | --- |
| `revolt-actor` | 在指定 server/channel 发送消息和 @ watcher。 |
| `revolt-watcher-bot` | ChatRSS 托管 bot，检查消息/mentions。 |
| `revolt-action-bot` | 后续真实回复；MVP 先 dry-run。 |

优先入口：

- Revolt bot token；
- 若可用 websocket gateway，优先 gateway；否则以 REST polling 做 MVP；
- 先限定单 server + 单 channel。

第一批规则：

```yaml
- name: revolt-mention-to-agent
  source: revolt
  connector: revolt.channel_messages
  when:
    mentioned: true
    account: revolt-watcher-bot
    channel: multi-agent-practice
  context:
    read_channel_window: true
    max_messages: 50
  actions:
    - agent.run
    - revolt.message.draft
```

### 2.4 GitHub

实践对象：issue、PR、comment、mention、review request。

建议账号：

| 账号 | 用途 |
| --- | --- |
| `github-actor` | 创建 issue/PR/comment 并 @ watcher。 |
| `github-watcher` | ChatRSS 托管 token，读取 notifications / issue / PR / comments。 |
| `github-action` | 后续真实评论或 review；MVP 先 dry-run。 |

优先入口：

- RSSHub routes：适合 repo-level issue/PR/comment 项目进展；
- GitHub notifications API：适合“有人 @ watcher”这个账号维度 trigger；
- GitHub REST/GraphQL：读取 issue/PR/comment 关联上下文。

第一批规则：

```yaml
- name: github-mention-to-agent
  source: github
  connector: github.notifications
  when:
    reason: mention
    account: github-watcher
  context:
    read_thread: true
  actions:
    - agent.run
    - github.comment.draft

- name: github-project-progress
  source: rsshub
  connector: comments
  when:
    repo: ChatArch/ChatRSS
  context:
    read_thread: true
  actions:
    - internal.notify
    - agent.run
```

### 2.5 Gitea

实践对象：issue、PR、comment、mention、assigned/review requested。

建议账号：

| 账号 | 用途 |
| --- | --- |
| `gitea-actor` | 创建 issue/PR/comment 并 @ watcher。 |
| `gitea-watcher` | ChatRSS 托管 token，读取 notifications / issue / PR。 |
| `gitea-action` | 后续真实评论；MVP 先 dry-run。 |

优先入口：

- Gitea API token；
- notifications endpoint / issues / pulls / comments polling；
- 如果实例有 webhook 权限，再补 webhook connector。

第一批规则：

```yaml
- name: gitea-mention-to-agent
  source: gitea
  connector: gitea.notifications
  when:
    reason: mention
    account: gitea-watcher
  context:
    read_thread: true
  actions:
    - agent.run
    - gitea.comment.draft
```

## 3. 统一 Trigger 任务定义

每个 trigger job 至少包含：

```yaml
id: github-watcher-mentions
source: github
connector: github.notifications
account: github-watcher
poll:
  interval_seconds: 60
  cursor: persisted
filter:
  reason: mention
dedupe:
  key: notification.id
context:
  read_thread: true
route_to: router.default
```

关键字段：

| 字段 | 作用 |
| --- | --- |
| `source` | 平台：discourse/zulip/revolt/github/gitea/rsshub。 |
| `connector` | 具体入口：notifications/messages/feed/comments。 |
| `account` | 使用哪个 watcher/bot 账号读取。 |
| `poll` | 轮询间隔和 cursor。 |
| `filter` | trigger 层轻量过滤，如 mention、sender、repo、channel。 |
| `dedupe` | 去重 key。 |
| `context` | 是否读取关联 thread/topic/message window。 |
| `route_to` | 进入哪个 router。 |

## 4. 最小实践顺序

### 本地闭环

- 用 `chatrss flow demo` 跑通 sample event。
- 验证 ledger 里有 `event_received`、`route_decision`、`action_planned`、`action_result`。

### GitHub / RSSHub 项目进展

- 选 `ChatArch/ChatRSS` 或另一个低风险 repo。
- RSSHub 订阅 issue/PR/comments。
- 新建测试 issue/comment 或使用已有公开更新。
- 验证 ChatRSS 生成标准 Event 和 dry-run action。

### GitHub 或 Gitea mention notification

- 建 watcher 账号/token。
- actor 账号 @ watcher。
- trigger 用 watcher token 轮询 notifications。
- 验证能捕获 mention，并读取 thread context。

### 首个社区平台：Zulip / Discourse / Revolt 三选一

优先选 API 最容易的一个做第一社区实践：

1. 建 actor + watcher/bot。
2. 在指定空间发一条含 @ watcher 的消息。
3. watcher connector 捕获消息。
4. Router 输出 `agent.run` + draft reply action；如果已授权，可执行平台 reply action。
5. Ledger 记录完整链路，并在执行写动作时追加 `action_verified`。

### 三个社区平台补齐

把首个社区实践中的 connector contract 复用到 Discourse、Zulip、Revolt。

## 5. 安全和状态边界

- API Key / bot token 只放本机或服务器安全配置，不写入 repo、progress、ledger。
- Ledger 记录账号别名和平台 ID，不记录 token。
- 外部写动作默认 `draft` 或 `approval_required`。
- Action 必须有 `idempotency_key`，不盲目重试。
- 如果 action 可能已执行但结果不明，进入 `RESULT_UNKNOWN`，人工核对。

## 6. 成功标准

每个平台完成时都要能展示：

1. actor 在平台上发出一个真实 trigger；
2. watcher 账号/token 能收到或轮询到这个信号；
3. ChatRSS 标准化出 TriggerEvent；
4. Router 明确说明为什么 act/archive/ignore；
5. Action Planner 产生 dry-run/draft action，或在明确授权后产生可执行 action；
6. Executor 写回平台后可由 watcher 回读验证；
7. Ledger 可回读完整因果链。
