# Changelog

## 2026-08-05

### Added

- Added a `chatrss flow demo` command that runs a local trigger-router-action MVP: sample trigger event → normalized schema → rule/model router → dry-run actions → JSONL ledger.
- Added shared event/action schema and a minimal pipeline module for future RSSHub, community, and project-progress trigger connectors.
- Added `docs/trigger-router-action.md` with the initial architecture and practice-source plan.
- Added a Zulip @mention quick start report from `zhihong.oray`: two accounts, watcher API polling, mention detection, event normalization, routing, dry-run actions, and ledger verification.
- Added ChatTea-style MkDocs documentation structure: scenario hub, CLI tree, capability map, interface tree, quick start, bilingual page mirrors, ChatArch Pages URLs, and preview workflow URL alignment.
- Added a real-world Zulip case: actor mention -> watcher trigger -> normalized event -> router decision -> Codex-plan research worker -> `zulip.message.reply` action bot reply -> ledger verification.
- Added a real-world Discourse case: `RexWang` topic/post -> `discourse.posts` TriggerEvent -> route decision -> `discourse.post.reply` action bot reply -> web readback verification.
- Added a real-world Mattermost case: `RexWang` @`hermes-agent` in `agent-lab/agent-room` -> `mattermost.posts` event -> `mattermost.thread_reply` bot reply, documenting when direct Mattermost gateway is simpler than ChatRSS.
- Split platform evidence into independent Zulip, Discourse, and Mattermost Markdown pages with RexWang-aligned conversation screenshots.

### Changed

- Bounded ChatArch internal dependencies for release: `chatstyle>=0.1.1,<0.2.0` and `chatenv>=0.2.3,<0.3.0`.

### Fixed

- Corrected README documentation-map wording so Zulip, Discourse, and Mattermost are all listed consistently in the real-platform case links.

## 2026-05-21

### Changed

- `watch` 处理机制改为任务导向：`issue` / `pull` / `comments` 会进入通知和文档事件日志。
- `repo_event` 保持背景记录，只落本地 JSONL，避免噪音。
- 飞书通知文案增加处理提示：先完成当前任务，再看是否需要整理/封装。

## YYYY-MM-DD

### Added

### Changed

### Fixed
