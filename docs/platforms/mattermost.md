# Mattermost 平台案例

Mattermost 是这三个平台里最适合“直接拉 Agent 进去”的实时聊天入口。它已经有 bot account、REST API v4、WebSocket、channel @mention、thread reply 等原生能力，因此 **chat-native Agent 场景优先走 Hermes/Mattermost gateway，不需要先绕 RSSHub**。

![Mattermost RexWang 对话证据截图](../assets/platform-cases/mattermost-rexwang-conversation.png)

## 当前验证状态

| 字段 | 值 |
| --- | --- |
| 平台 | Mattermost Team Edition |
| Public URL | https://matter.public.wzhecnu.cn |
| Local short alias | `matter.local.wzhecnu.cn`（裸 `matter.local` 当前不解析） |
| Team / Channel | `agent-lab` / `agent-room` |
| Actor | `RexWang`（Mattermost username: `rexwang`） |
| Bot | `hermes-agent` |
| Trigger post | https://matter.public.wzhecnu.cn/agent-lab/pl/q7xk8wq3q3rbugodkdw6u8cuka |
| Reply post | https://matter.public.wzhecnu.cn/agent-lab/pl/9okz731eapf47jks96p87eo8ze |
| Event id | `mattermost:post:q7xk8wq3q3rbugodkdw6u8cuka:mention:hermes-agent` |
| Action | `mattermost.thread_reply` |
| Evidence screenshot | `docs/assets/platform-cases/mattermost-rexwang-conversation.png` |

## 触发机制

```text
RexWang 在 Mattermost agent-room 中 @hermes-agent
  -> Mattermost 产生真实 post event
  -> Hermes/Mattermost gateway 可直接通过 WebSocket 收到事件
  -> 或 ChatRSS mattermost.posts connector 将 post 标准化为 TriggerEvent
  -> router 判定 act
  -> hermes-agent 在 Mattermost thread 中真实回复
  -> ledger 记录 trigger/action/readback
```

这里的 **前置动作** 是 `RexWang @hermes-agent`。行动内容来自 Mattermost post 正文。

## 是否需要 ChatRSS？

结论：**如果目标只是让 Agent 进入 Mattermost 房间，优先不需要 ChatRSS；直接走 Hermes/Mattermost gateway 更简单。**

Mattermost 已经提供实时 agent 入口：

```text
Mattermost WebSocket / REST API
  -> Hermes Mattermost gateway
  -> allowed users/channels / require mention
  -> agent run
  -> thread reply
```

ChatRSS 仍然有价值，但它的位置变成“统一事件层 / 审计层 / 跨平台 router”：

```text
Mattermost post/webhook/WebSocket event
  -> mattermost.posts connector
  -> TriggerEvent
  -> Rule Router / Model Router
  -> optional Action Planner
  -> Ledger
```

也就是说：**Mattermost 可以不经过 RSSHub；但如果要把 Zulip、Discourse、Mattermost、GitHub feed 都放进同一套去重、路由、审计和 action ledger，ChatRSS 仍然是统一入口。**

## 标准事件

```json
{
  "source": "mattermost",
  "connector": "mattermost.posts",
  "event_type": "community.mention.created",
  "event_id": "mattermost:post:q7xk8wq3q3rbugodkdw6u8cuka:mention:hermes-agent",
  "actor": {
    "type": "mattermost_user",
    "username": "rexwang",
    "display_name": "RexWang"
  },
  "subject": {
    "type": "mattermost.post",
    "team": "agent-lab",
    "channel": "agent-room",
    "post_id": "q7xk8wq3q3rbugodkdw6u8cuka"
  },
  "raw": {
    "mentions": ["hermes-agent"],
    "marker": "chatrss-mattermost-trigger-20260805043149"
  }
}
```

## 当前部署已准备好的接入键

Mattermost 服务侧已经准备过 Hermes gateway 的 bot env，路径是：

```text
/home/zhihong/.chatarch/mattermost/secrets/bot.env
```

公开文档只列键名，不列值：

```text
MATTERMOST_URL
MATTERMOST_TOKEN
MATTERMOST_BOT_USERNAME
MATTERMOST_ALLOWED_USERS
MATTERMOST_HOME_CHANNEL
MATTERMOST_REPLY_MODE
MATTERMOST_REQUIRE_MENTION
```

## 推荐用法

### 直接 Agent 房间

适合实时协作：

```text
RexWang @hermes-agent
  -> Hermes Mattermost gateway
  -> agent 回复 thread
```

这是最简单路径。

### ChatRSS 统一 router

适合跨平台审计：

```text
Mattermost connector
  -> TriggerEvent
  -> Router
  -> shared Ledger
  -> optional Mattermost action executor
```

这种模式用于把 Mattermost 和 Zulip、Discourse、GitHub/RSSHub feed 放进同一张事件账本。
