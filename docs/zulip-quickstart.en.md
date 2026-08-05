# Zulip @mention Quick Start

This quick start verifies the first real platform trigger for ChatRSS: one Zulip account sends a message mentioning a ChatRSS-managed watcher account; the watcher account polls Zulip with its own API key; ChatRSS normalizes the mention into an event, routes it, plans dry-run actions, and writes a ledger.

## What was verified

Host: `zhihong.oray`

Platform:

- Zulip URL: `https://zulip.public.wzhecnu.cn`
- Stream: `chatrss-quickstart`
- Topic: `trigger-router-action`

Accounts:

| account | role |
| --- | --- |
| `chatrss-actor@chatarch.local` | Sends the test message. |
| `chatrss-watcher@chatarch.local` / `ChatRSS Watcher Bot` | ChatRSS-managed watcher; polls Zulip and detects mentions. |

The watcher credentials and API key are stored only in the task-local secrets file on the host with mode `0600`; no password or API key is stored in this repository.

## Flow

```text
ChatRSS Actor
  -> sends a Zulip stream message mentioning @ChatRSS Watcher Bot
  -> Watcher polls Zulip messages API using its own API key
  -> Zulip message flags include mentioned
  -> ChatRSS normalizes the message into TriggerEvent
  -> Router/model stub decides act
  -> Action planner produces dry-run actions
  -> JSONL ledger records the whole chain
```

Verified message:

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
  "event_id": "zulip:message:16:mention:chatrss-watcher@chatarch.local",
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

## Router/action result

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

All actions were dry-run/draft only:

| action | result | external write |
| --- | --- | --- |
| `internal.notify` | `DRY_RUN_OK` | false |
| `agent.run` | `DRY_RUN_OK` | false |
| `zulip.message.draft` | `DRY_RUN_OK` | false |

## Host artifacts

On `zhihong.oray`:

```text
/home/zhihong/Playground/projects/chatrss/08-05-zulip-trigger-quickstart/scripts/zulip_trigger_quickstart.py
/home/zhihong/Playground/projects/chatrss/08-05-zulip-trigger-quickstart/reports/zulip-quickstart.md
/home/zhihong/Playground/projects/chatrss/08-05-zulip-trigger-quickstart/reports/zulip-quickstart-result.json
/home/zhihong/Playground/projects/chatrss/08-05-zulip-trigger-quickstart/playground/zulip-mention.ledger.jsonl
```

The reusable implementation target for ChatRSS is a future `zulip.messages` connector backed by a trigger job like:

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
