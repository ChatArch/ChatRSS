# Zulip @mention 快速开始

这条 quick start 验证了 ChatRSS 的真实 Zulip trigger：一个 Zulip 账号发送消息并 @ ChatRSS 托管的 watcher 账号；watcher 账号用自己的 API key 轮询 Zulip；ChatRSS 把 mention 标准化为 Event，进入 router，规划 action，并写入 ledger。完整的 actor -> watcher -> worker -> action bot 回帖案例见 [真实事件案例](real-world-cases.md)。

## 已验证对象

环境：受控 Zulip 服务环境（公开入口 + 私有凭据存储）

平台：

- Zulip URL：`https://zulip.public.wzhecnu.cn`
- Stream：`chatrss-quickstart`
- Topic：`trigger-router-action`

账号：

| account | role |
| --- | --- |
| `watcher@example.invalid` | 发送测试消息。 |
| `watcher@example.invalid` / `ChatRSS Watcher Bot` | ChatRSS 托管 watcher；轮询 Zulip 并检测 mention。 |
| `watcher@example.invalid` / `ChatRSS Agent Bot` | 真实回帖案例中的 action account；默认不启用外部写动作。 |

watcher credential 和 API key 只保存在 host 上 task-local secrets 文件，权限为 `0600`；仓库中不保存 password 或 API key。

## 流程

```text
ChatRSS Actor
  -> 发送一条 Zulip stream 消息并 @ChatRSS Watcher Bot
  -> Watcher 用自己的 API key 轮询 Zulip messages API
  -> Zulip message flags 包含 mentioned
  -> ChatRSS 标准化成 TriggerEvent
  -> Router/model stub 判断 act
  -> Action planner 产生 dry-run actions
  -> JSONL ledger 记录完整链路
```

已验证消息：

```text
message_id: 16
permalink: https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/16
watcher_detected: true
mention_flag: true
```

## Event envelope

```json
{
  "source": "zulip",
  "connector": "zulip.messages",
  "event_type": "community.mention.created",
  "event_id": "zulip:message:16:mention:watcher@example.invalid",
  "subject": {
    "type": "zulip.message",
    "stream": "chatrss-quickstart",
    "topic": "trigger-router-action",
    "message_id": 16
  },
  "raw": {
    "mentioned": true,
    "flags": ["mentioned"]
  }
}
```

## Router / action result

```json
{
  "decision": "act",
  "model_used": "rule-router + deterministic model stub",
  "actions": [
    "internal.notify",
    "agent.run",
    "zulip.message.draft"
  ],
  "requires_approval": true
}
```

所有 action 都是 dry-run / draft：

| action | result | external write |
| --- | --- | --- |
| `internal.notify` | `DRY_RUN_OK` | false |
| `agent.run` | `DRY_RUN_OK` | false |
| `zulip.message.draft` | `DRY_RUN_OK` | false |

## 验证产物

验证脚本、ledger、JSON 结果和报告保存在私有任务 project 中。公开文档只保留非敏感的 message id、event id、action type 和流程摘要；不记录主机名、home path、凭据文件路径或 secret key 名。

后续进入 ChatRSS 的可复用目标是 `zulip.messages` connector，对应 trigger job：

```yaml
id: zulip-watcher-mention
source: zulip
connector: zulip.messages
account: zulip-watcher
poll:
  interval_seconds: 30
  cursor: newest
filter:
  mentioned: true
  stream: chatrss-quickstart
context:
  read_topic: true
  max_messages: 50
actions:
  - internal.notify
  - agent.run
  - zulip.message.draft
```


## 完整真实回帖案例

Quick start 的最小验收可以停在 `dry-run` / `draft` action；已验证的完整案例进一步执行了真实回帖：

| 字段 | 值 |
| --- | --- |
| Actor message | https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/20 |
| Reply message | https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/21 |
| Event id | `zulip:message:20:mention:watcher@example.invalid` |
| Action result | `SENT external_write=true message_id=21` |

这次 actor 提出的任务是让 worker 分析 OpenAI Codex 在普通账号、ChatGPT Plus、ChatGPT Pro 三种 coding 使用方案上的差异。ChatRSS 捕获 mention、路由为 `act`、执行资料核对 worker，然后由 action bot 把结果回帖到同一个 Zulip topic。完整事件、标准事件 envelope、路由决策和 ledger 顺序见 [真实事件案例](real-world-cases.md)。
