# Real-World Event Cases

This page records how ChatRSS moves from an abstract trigger-router-action demo to real platform loops. The important point is that the task starts as a real platform event: a user-visible message, topic, post, or mention triggers ChatRSS, a worker completes the task, and an action bot writes back. Zulip @mentions and Discourse topic/posts are now both verified community-platform shapes.

## Case: Zulip @mention triggers a Codex plan analysis

| Field | Value |
| --- | --- |
| Platform | Zulip |
| Stream | `chatrss-quickstart` |
| Topic | `trigger-router-action` |
| Actor message | https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/20 |
| Reply message | https://zulip.public.wzhecnu.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/21 |
| Trigger marker | `codex-plan-20260805012352` |
| Event id | `zulip:message:20:mention:chatrss-watcher@chatarch.local` |
| Action | `zulip.message.reply` |
| Verification | watcher readback confirmed reply message `21` |

### The real user message

The actor posted a real Zulip message in the topic and mentioned the ChatRSS watcher:

```text
@ChatRSS Watcher Bot real task codex-plan-20260805012352:
Please analyze the differences between OpenAI Codex on a regular account,
ChatGPT Plus, and ChatGPT Pro for coding use: entry points, quota/priority,
suitable tasks, and main limitations. Route it through the ChatRSS trigger,
let an agent complete the analysis, and reply in this Zulip topic.
```

The task therefore exists first as a platform event. ChatRSS can only proceed through the message that the watcher account can see.

### Background execution chain

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

### Normalized event

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

### Route decision

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

### Worker reply summary

The worker did not hard-code daily or monthly quota numbers because OpenAI plan limits change. It fixed the structural differences instead:

| Plan | Entry point | Good fit | Main limitation |
| --- | --- | --- | --- |
| Regular / unpaid account | Do not assume included Codex quota; check whether Codex Web is available or use the API-key path | Trials, occasional small tasks, CLI smoke tests | Not suitable for dependable included quota; API-key usage is separate from ChatGPT subscription quota |
| ChatGPT Plus | Choose `Sign in with ChatGPT` in the `codex` CLI, or use Codex Web | Personal daily coding: reading code, small changes, tests, PR explanations | Included quota exists but is usually not the highest; heavy parallel or long tasks can hit limits sooner |
| ChatGPT Pro | Same ChatGPT sign-in and Codex Web paths | Frequent, long-running, agentic coding: larger repositories, multi-step implementation, more cloud Codex usage | Higher cost; exact quota should be checked in the account's live plan/usage page |

The main public source used by the worker was OpenAI's Codex repository: <https://github.com/openai/codex>. Its README describes Codex CLI as a local coding agent, Codex Web as the cloud-based agent, ChatGPT sign-in for Plus/Pro/Business/Edu/Enterprise plan usage, and an API-key alternative.

### Ledger records

The full event ledger records a real reply action, not just a dry-run action:

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

Internal ledgers, reports, and secrets stay in the task project. Public docs record only non-sensitive message ids, public URLs, event types, and action results. Passwords and API keys stay in the host-side `secrets/` directory and were checked for report/playground/script leakage.


## Case: Discourse topic/post triggers an Agent Runs reply

| Field | Value |
| --- | --- |
| Platform | Discourse |
| Category | `Agent Runs` |
| Actor | `RexWang` / user id `4` / ordinary user |
| Actor post | https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/1 |
| Reply post | https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/2 |
| Trigger marker | `chatrss-discourse-trigger-20260805022954` |
| Event id | `discourse:post:25:mention:system` |
| Action | `discourse.post.reply` |
| Verification | RexWang's logged-in session read the topic JSON and confirmed post `25` and reply `26` both contain the marker |

### The real user post

`RexWang` is the ordinary Discourse user created and verified for this practice. In the run, `RexWang` created a real topic in the `Agent Runs` category and mentioned `@system` in the first post:

```text
@system This is a real ChatRSS Discourse trigger practice created by RexWang.

Marker: `chatrss-discourse-trigger-20260805022954`

Task: show how a Discourse topic/post can become a ChatRSS TriggerEvent,
then route to an agent action.
```

### Background execution chain

```text
Discourse topic/post by RexWang
  -> discourse.posts watcher reads topic/post metadata plus raw/cooked content
  -> TriggerEvent(source=discourse, connector=discourse.posts, event_type=community.mention.created)
  -> Router decision: act
  -> action plan: discourse.post.reply
  -> action bot writes a real Discourse reply in the same topic
  -> RexWang login session reads back the topic JSON
  -> JSONL ledger records the full chain
```

### Normalized event

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

### Route decision and action

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

The action executor used Discourse's own `PostCreator` to write a real reply. It is not a mock JSON fixture and not a direct SQL insert. The reply account was `ark-code-latest1`, and the reply post id is `26`.

### Ledger records

```text
actor_topic_created
event_received
route_decision
action_planned: discourse.post.reply
action_result: sent external_write=true post_id=26
action_verified: actor_post_exists=true reply_exists=true
```

Internal Discourse reports keep only non-sensitive evidence. Public docs record URLs, post ids, event ids, action types, and verification status; they do not record passwords, sessions, cookies, API keys, or admin tokens.

## Connector acceptance contract

The Zulip case gives every future platform connector a minimum acceptance contract:

1. A user creates a real task on the platform: issue, comment, topic message, chat message, or feed item.
2. A watcher reads only platform-visible events through an API token, bot token, webhook secret, RSS/RSSHub route, or notification API.
3. The trigger emits a normalized event and does not call actions directly.
4. The router decides whether to work.
5. The worker produces an auditable result with source and context evidence.
6. The action account writes back to the platform when explicitly allowed.
7. The ledger connects event, decision, worker result, action result, and verification.
