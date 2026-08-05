# ChatRSS Capability Map

The capability map answers what ChatRSS owns and what it does not own. Invocation details are in the [CLI tree](cli-tree.en.md); Python mappings are in the [interface tree](interface-tree.en.md).

## Current capability surface

| Capability | Current status | Current entry point | Minor-version target |
| --- | --- | --- | --- |
| RSSHub/GitHub feed connector | Implemented through the legacy watcher path | `chatrss init` / `chatrss watch` | Move under `trigger add/test/run` |
| Event Schema | `TriggerEvent` / `ActionJob` / `RouteDecision` implemented | `chatrss.events` | Every connector emits this envelope |
| Rule Router | Minimal rules implemented | `chatrss.pipeline.route_event` | Configurable YAML/JSON rules before model routing |
| Model Router | Deterministic stub implemented | `chatrss.pipeline.model_route_event` | LLM JSON decision with schema validation and explanations |
| Action Planner | Dry-run planning implemented | `chatrss.pipeline.plan_actions` | Action outbox with idempotency keys |
| Action Executor | Dry-run executor implemented | `chatrss.pipeline.execute_action` | Feishu/GitHub/Gitea/Zulip/agent adapters |
| Ledger | JSONL flow ledger implemented | `append_ledger` / `read_ledger` | SQLite/Postgres inbox/outbox/ledger with replay and audit |
| Real community trigger | Zulip @mention quick start verified | docs and host-side practice script | Zulip/Discourse/Revolt connectors |

## Responsibility boundaries

<div class="grid cards" markdown>

- **Trigger Connector**

  Reads RSS, RSSHub, webhooks, notification APIs, or community message APIs and emits standard Events only.

- **Router / Model**

  Rules reduce noise first; models decide intent, priority, required context, and action type.

- **Action / Ledger**

  The planner emits jobs; the executor runs adapters; the ledger provides audit, idempotency, and recovery.

</div>

## Explicit non-goals

- ChatRSS does not turn RSSHub into a workflow engine; RSSHub is a trigger stream provider.
- Trigger connectors do not directly send messages, comment, merge, publish, or edit configuration.
- Planned commands are not successful placeholder CLI commands.
- Ledgers, reports, README files, and docs must not contain tokens, passwords, or API keys.
- External writes are not executed by default; they must pass through dry-run/draft/approval stages.

## Platform extension priority

| Source | Preferred entry | First action |
| --- | --- | --- |
| GitHub project progress | RSSHub routes / comments / issue / PR | notify + agent.run + comment draft |
| Gitea collaboration events | notifications API / issue / PR comments | agent.run + gitea.comment.draft |
| Zulip community messages | messages/events API + mention flag | agent.run + zulip.message.draft |
| Discourse forum | notifications/topics/posts API | agent.run + discourse.reply.draft |
| Revolt channels | bot token + gateway or REST polling | agent.run + revolt.message.draft |
