# ChatRSS Documentation

ChatRSS is an RSS / RSSHub-first agent trigger tool. It normalizes feeds, notifications, community messages, and code-hosting events into Events, then routes them through Router, Model, Action, and Ledger stages.

Site: <https://arch.gh.wzhecnu.cn/ChatRSS/>

## Choose by scenario

| Scenario | Documentation |
| --- | --- |
| Run the local flow quickly | [Quick start](quickstart.en.md) |
| Inspect current and target commands | [CLI tree](cli-tree.en.md) |
| Check what ChatRSS owns | [Capability map](capability-map.en.md) |
| Map CLI commands to Python APIs | [Interface tree](interface-tree.en.md) |
| Understand Trigger / Schema / Router / Model / Action / Ledger | [Trigger-Router-Action design](trigger-router-action.md) |
| Pick a real platform trigger practice | [Real platform practice plan](practice-plan.md) |
| Review a real platform loop | [Real-world cases](real-world-cases.en.md) / [Zulip @mention quick start](zulip-quickstart.en.md) |

## Documentation sections

<div class="grid cards" markdown>

- **Getting started**

  Install locally, run `flow demo`, inspect RSSHub feed watching, and understand the RSSHub server boundary.

- **Commands and interfaces**

  ChatTea-style CLI tree, target minor-version tree, capability map, and Python interface mapping.

- **Architecture**

  Durable `Trigger -> Event Schema -> Router -> Model -> Action -> Ledger` abstraction.

- **Practice**

  Zulip and Discourse are verified real trigger/action cases; Revolt, GitHub, and Gitea follow the same pattern.

</div>

## Current safety defaults

- Triggers discover and normalize events; they do not execute external actions directly.
- `repo_event` is archived as background context by default.
- External writes default to `dry_run`, `draft`, or `approval_required`.
- Ledgers record events, decisions, actions, and results, not tokens, passwords, or API keys.

## Local preview

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```
