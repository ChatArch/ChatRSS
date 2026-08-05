# 真实事件案例

这一页记录 ChatRSS 从“抽象 trigger-router-action demo”走到真实平台闭环的实践案例。重点不是手动复制一段结果，而是让平台上的真实事件触发 ChatRSS，然后由 worker 完成任务并通过 action bot 回帖。当前已验证 Zulip @mention 和 Discourse topic/post 两种社区平台形态。

## 案例：Zulip @mention 触发 Codex 方案分析

| 字段 | 值 |
| --- | --- |
| 平台 | Zulip |
| Stream | `chatrss-quickstart` |
| Topic | `trigger-router-action` |
| Actor message | https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/20 |
| Reply message | https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/21 |
| Trigger marker | `codex-plan-20260805012352` |
| Event id | `zulip:message:20:mention:chatrss-watcher@chatarch.local` |
| Action | `zulip.message.reply` |
| Verification | watcher readback confirmed reply message `21` |

### 用户真实发帖

Actor 在 Zulip topic 中发送一条真实消息，并 @ ChatRSS 托管的 watcher：

```text
@ChatRSS Watcher Bot 真实任务 codex-plan-20260805012352:
请分析一下 OpenAI Codex 在普通账号、ChatGPT Plus、ChatGPT Pro
三种 coding 使用方案上的区别：入口、额度/优先级、适合任务、主要限制分别是什么？
请通过 ChatRSS trigger 后让 agent 完成分析，并把结果回帖到这个 Zulip topic。
```

这一步的关键是：用户任务先存在于平台事件里，而不是由 Agent 私下接收一个隐藏指令。ChatRSS 只能通过 watcher 能看到的 Zulip 消息进入后续流程。

### 后台执行过程

```text
Zulip actor message
  -> @ ChatRSS Watcher Bot
  -> watcher API polling detects flags=[mentioned]
  -> TriggerEvent(source=zulip, connector=zulip.messages, event_type=community.mention.created)
  -> Router decision: act
  -> worker: codex-plan-analysis
  -> source fetch + bounded synthesis
  -> action plan: zulip.message.reply
  -> action bot posts the answer back to the same topic
  -> watcher reads back the reply
  -> JSONL ledger records the full chain
```

### 标准事件

```json
{
  "source": "zulip",
  "connector": "zulip.messages",
  "event_type": "community.mention.created",
  "event_id": "zulip:message:20:mention:chatrss-watcher@chatarch.local",
  "subject": {
    "type": "zulip.message",
    "stream": "chatrss-quickstart",
    "topic": "trigger-router-action",
    "message_id": 20
  },
  "raw": {
    "mentioned": true,
    "flags": ["mentioned"]
  }
}
```

### 路由决策

```json
{
  "decision": "act",
  "model_used": "rule-router + bounded research worker",
  "reason": "Watcher was @mentioned with a Codex plan comparison request; start the research worker and reply to the same Zulip topic.",
  "actions": [
    "internal.notify",
    "agent.run",
    "zulip.message.reply"
  ],
  "requires_approval": false
}
```

### Worker 回帖摘要

Worker 回帖没有写死每日/月度任务数，因为 OpenAI 的 plan limit 会变化；它只固定结构性差异：

| 方案 | 入口 | 适合什么 | 主要限制 |
| --- | --- | --- | --- |
| 普通账号 / 未付费账号 | 不应假设有计划内 Codex 额度；可看账户是否开放 Codex Web，或走 API key 路径 | 试用、偶发小任务、验证 CLI 是否可跑 | 不适合依赖稳定额度；API key 路径和 ChatGPT 订阅额度是两套东西 |
| ChatGPT Plus | `codex` CLI 里选择 `Sign in with ChatGPT`，或使用 Codex Web | 个人日常 coding：读代码、改小功能、写测试、解释 diff | 有计划内额度但通常不是最高；大量并行/长任务会更容易撞到限额 |
| ChatGPT Pro | 同样通过 ChatGPT 登录/Codex Web | 高频、长时间、重型 agentic coding：多轮实现、较大仓库分析、更多并发任务 | 费用更高；具体限额仍以账户内实时 plan/usage 页面为准 |

Worker 使用的主要公开来源是 OpenAI 的 Codex repository：<https://github.com/openai/codex>。该 README 说明 Codex CLI 是本地 coding agent，Codex Web 是云端 agent，推荐通过 ChatGPT 登录把 Codex 作为 Plus、Pro、Business、Edu 或 Enterprise 计划的一部分使用，也可走 API key 路径。

### Ledger 记录

这次完整事件的 ledger 不是只写 dry-run action，而是记录了真实回帖动作：

```text
actor_message_sent
event_received
route_decision
agent_started
source_fetched
agent_result
action_planned: zulip.message.reply
action_result: SENT external_write=true message_id=21
action_verified: visible_to_watcher=true
```

> 注：内部 ledger/report/secrets 文件保存在任务 project 中；公开文档只记录非敏感 message id、公开 URL、事件类型和动作结果。密码/API key 只保存在本地 `secrets/`，并已做泄露扫描。


## 案例：Discourse topic/post 触发 Agent Runs 回帖

| 字段 | 值 |
| --- | --- |
| 平台 | Discourse |
| Category | `Agent Runs` |
| Actor | `RexWang` / user id `4` / 普通用户 |
| Actor post | https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/1 |
| Reply post | https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/2 |
| Trigger marker | `chatrss-discourse-trigger-20260805022954` |
| Event id | `discourse:post:25:mention:system` |
| Action | `discourse.post.reply` |
| Verification | RexWang 登录态回读 topic JSON，确认 post `25` 和 reply `26` 都包含 marker |

### 用户真实发帖

`RexWang` 是本次实践创建并验证的 Discourse 普通用户，账号已通过网页登录接口校验。实践里，`RexWang` 在真实 Discourse `Agent Runs` 分类创建 topic，并在首帖中 @ `system`：

```text
@system This is a real ChatRSS Discourse trigger practice created by RexWang.

Marker: `chatrss-discourse-trigger-20260805022954`

Task: show how a Discourse topic/post can become a ChatRSS TriggerEvent,
then route to an agent action.
```

### 后台执行过程

```text
Discourse topic/post by RexWang
  -> discourse.posts watcher reads topic/post metadata and raw/cooked content
  -> TriggerEvent(source=discourse, connector=discourse.posts, event_type=community.mention.created)
  -> Router decision: act
  -> action plan: discourse.post.reply
  -> action bot writes a real Discourse reply in the same topic
  -> RexWang login session reads back the topic JSON
  -> JSONL ledger records the full chain
```

### 标准事件

```json
{
  "source": "discourse",
  "connector": "discourse.posts",
  "event_type": "community.mention.created",
  "event_id": "discourse:post:25:mention:system",
  "subject": {
    "kind": "post",
    "id": 25,
    "topic_id": 18,
    "post_number": 1,
    "category": "Agent Runs",
    "url": "https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/1"
  },
  "actor": {
    "kind": "user",
    "id": 4,
    "username": "RexWang"
  },
  "payload": {
    "mentions": ["system"],
    "marker": "chatrss-discourse-trigger-20260805022954"
  }
}
```

### 路由决策与动作

```json
{
  "decision": "act",
  "route": "community.discourse.mention",
  "model_used": "rule-router + deterministic practice worker",
  "actions": [
    "internal.notify",
    "agent.run",
    "discourse.post.reply"
  ]
}
```

Action executor 使用 Discourse 自身的 `PostCreator` 写入真实 reply，不是 mock JSON，也不是直接 SQL 插入。回帖账号为 `ark-code-latest1`，reply post 为 `26`。

### Ledger 记录

```text
actor_topic_created
event_received
route_decision
action_planned: discourse.post.reply
action_result: sent external_write=true post_id=26
action_verified: actor_post_exists=true reply_exists=true
```

> 注：Discourse 站点当前登录后可读；公开文档只记录非敏感 URL、post id、event id、action type 和验证状态，不记录用户密码、session、cookie、API key 或管理员 token。

## 接入原则

这个案例形成了 ChatRSS 后续平台接入的最低验收标准：

1. **用户先在平台上发真实任务**：issue、comment、topic message、chat message 或 feed item。
2. **Watcher 只读平台事件**：通过 API token、bot token、webhook secret、RSS/RSSHub route 或 notification API 读取。
3. **Trigger 只产出事件**：connector 不直接调用 action。
4. **Router 决定是否工作**：规则先过滤，再进入 worker/model。
5. **Worker 产出可审计结果**：资料来源、任务输入、输出摘要要能回查。
6. **Action 通过平台账号回写**：回帖、评论、发文、创建 issue 等都要记录 `action_result`。
7. **Ledger 串起完整因果链**：从 `actor_message_sent` 到 `action_verified` 都能回放。
