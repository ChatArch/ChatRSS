"""Minimal trigger-router-action pipeline.

This module wires the new product abstraction end to end without adding a heavy
workflow runtime. The first slice is deliberately deterministic and dry-run only:
RSS/RSSHub feed items can be normalized into events, routed by rules plus a
model-like heuristic, planned into action jobs, executed as dry-runs, and written
to a JSONL ledger.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from chatrss.events import ActionJob, ActionResult, EventActor, EventSubject, RouteDecision, TriggerEvent
from chatrss.feed import FeedItem


_TASK_CONNECTORS = {"issue", "pull", "comments"}
_BACKGROUND_CONNECTORS = {"repo_event"}
_ACTION_KEYWORDS = (
    "agent",
    "task",
    "please",
    "review",
    "fix",
    "update",
    "reply",
    "请",
    "帮",
    "更新",
    "修复",
    "审阅",
    "回复",
    "留言",
    "任务",
    "模型",
)


@dataclass(frozen=True)
class Rule:
    """Simple exact-match rule for the first router slice."""

    name: str
    match: dict[str, Any]
    route_to: str
    action_hints: list[str] = field(default_factory=list)
    reason: str = ""


DEFAULT_RULES: tuple[Rule, ...] = (
    Rule(
        name="task-feed-to-model-router",
        match={"connector": sorted(_TASK_CONNECTORS)},
        route_to="model_router",
        action_hints=["notify"],
        reason="issue/pull/comments are task-bearing feed items",
    ),
    Rule(
        name="repo-event-background-only",
        match={"connector": sorted(_BACKGROUND_CONNECTORS)},
        route_to="archive_only",
        reason="repo_event is useful context but too noisy for active actions",
    ),
)


_EVENT_TYPE_BY_CONNECTOR = {
    "issue": "github.issue.item",
    "pull": "github.pull.item",
    "comments": "github.comment.item",
    "repo_event": "github.repo_event.item",
}


def default_ledger_path(name: str = "flow") -> Path:
    """Return the default JSONL ledger path under CHATARCH_HOME."""

    base = Path(os.environ.get("CHATARCH_HOME", Path.home() / ".chatarch"))
    return base / "chatrss" / f"{name}.ledger.jsonl"


def event_from_feed_item(
    item: FeedItem,
    repo: str,
    *,
    source: str = "rsshub",
    actor: EventActor | None = None,
) -> TriggerEvent:
    """Normalize a parsed feed item into the shared TriggerEvent schema."""

    subject = _subject_from_link(item.link, repo, item.source)
    event_id = _stable_id(source, item.source, item.guid or item.link or item.title)
    return TriggerEvent(
        event_id=event_id,
        source=source,
        connector=item.source,
        event_type=_EVENT_TYPE_BY_CONNECTOR.get(item.source, "feed.item"),
        title=item.title,
        url=item.link,
        content=item.description,
        published_at=item.pub_date,
        actor=actor or EventActor(),
        subject=subject,
        raw={"guid": item.guid, "repo": repo},
    )


def sample_multi_agent_event() -> TriggerEvent:
    """Return a deterministic demo event for local end-to-end smoke tests."""

    return TriggerEvent(
        event_id="demo:rsshub:github.comments:chatarch-chatrss-12-456",
        source="rsshub",
        connector="comments",
        event_type="github.comment.item",
        title="New comment on ChatArch/ChatRSS#12",
        url="https://github.com/ChatArch/ChatRSS/issues/12#issuecomment-456",
        content="请 agent 读取关联讨论，更新文档，并准备一条回复草稿。",
        published_at="2026-08-05T10:00:00Z",
        actor=EventActor(type="github_user", id="important-user", display_name="important-user"),
        subject=EventSubject(type="github.issue", repo="ChatArch/ChatRSS", number="12"),
        raw={"demo": True},
    )


def route_event(event: TriggerEvent, rules: Iterable[Rule] = DEFAULT_RULES) -> RouteDecision:
    """Apply rule routing, then the MVP model-like router if requested."""

    for rule in rules:
        if _matches_rule(event, rule):
            if rule.route_to == "archive_only":
                return RouteDecision(
                    event_id=event.event_id,
                    decision="archive",
                    route=rule.route_to,
                    reason=rule.reason or f"matched rule {rule.name}",
                )
            if rule.route_to == "model_router":
                return model_route_event(event, base_hints=rule.action_hints, rule_name=rule.name)
            return RouteDecision(
                event_id=event.event_id,
                decision="ignore",
                route=rule.route_to,
                reason=rule.reason or f"matched rule {rule.name}",
                action_hints=list(rule.action_hints),
            )

    return RouteDecision(
        event_id=event.event_id,
        decision="ignore",
        route="no_rule",
        reason="no route rule matched",
    )


def model_route_event(
    event: TriggerEvent,
    *,
    base_hints: Iterable[str] = (),
    rule_name: str = "model_router",
) -> RouteDecision:
    """Deterministic stand-in for the future model router.

    The goal is to prove the integration seam. A real LLM router can later replace
    this function while preserving RouteDecision and ActionJob contracts.
    """

    text = f"{event.title}\n{event.content}".lower()
    hints = list(dict.fromkeys(base_hints))
    matched_keywords = [kw for kw in _ACTION_KEYWORDS if kw.lower() in text]

    if event.connector in _BACKGROUND_CONNECTORS:
        return RouteDecision(
            event_id=event.event_id,
            decision="archive",
            route=rule_name,
            reason="background connector should be archived",
        )

    if matched_keywords:
        hints.append("agent.run")
        if event.connector == "comments":
            hints.append("github.comment.draft")
        return RouteDecision(
            event_id=event.event_id,
            decision="act",
            route="action_planner",
            reason="model-router-stub detected task intent: " + ", ".join(matched_keywords[:5]),
            action_hints=list(dict.fromkeys(hints)),
            context={"matched_keywords": matched_keywords, "rule": rule_name},
        )

    if event.connector in _TASK_CONNECTORS:
        return RouteDecision(
            event_id=event.event_id,
            decision="act",
            route="action_planner",
            reason="task connector matched; notify for human triage",
            action_hints=list(dict.fromkeys(hints or ["notify"])),
            context={"rule": rule_name},
        )

    return RouteDecision(
        event_id=event.event_id,
        decision="ignore",
        route=rule_name,
        reason="no actionable intent detected",
    )


def plan_actions(event: TriggerEvent, decision: RouteDecision) -> list[ActionJob]:
    """Convert a route decision into concrete dry-run action jobs."""

    if decision.decision != "act":
        return []

    actions: list[ActionJob] = []
    for hint in decision.action_hints:
        if hint == "notify":
            actions.append(_action_job(event, "internal.notify", "dry_run", input={
                "text": f"[{event.connector}] {event.title}\n{event.url}",
            }))
        elif hint == "agent.run":
            actions.append(_action_job(event, "agent.run", "dry_run", input={
                "task": "Read the linked context and decide the next best response.",
                "event_title": event.title,
                "event_url": event.url,
            }))
        elif hint == "github.comment.draft":
            actions.append(_action_job(
                event,
                "github.comment",
                "draft",
                target=asdict(event.subject),
                input={
                    "body": "Draft a response after the agent has read the linked discussion.",
                    "source_event": event.url,
                },
                requires_approval=True,
            ))
    return actions


def execute_action(action: ActionJob, *, dry_run: bool = True) -> ActionResult:
    """Execute an action job.

    The MVP intentionally only supports dry-run execution. Real adapters should be
    added behind this boundary after authorization and idempotency are designed.
    """

    if not dry_run:
        return ActionResult(
            action_id=action.action_id,
            status="NEEDS_ADAPTER",
            message=f"No real executor is registered for {action.type}",
            receipt={"type": action.type, "mode": action.mode},
            verified=False,
        )

    return ActionResult(
        action_id=action.action_id,
        status="DRY_RUN_OK",
        message=f"Would execute {action.type} in {action.mode} mode",
        receipt={
            "type": action.type,
            "mode": action.mode,
            "idempotency_key": action.idempotency_key,
            "requires_approval": action.requires_approval,
        },
        verified=True,
    )


def run_event_flow(event: TriggerEvent, ledger_path: Path, *, dry_run: bool = True) -> dict[str, Any]:
    """Run one event through router, planner, executor, and ledger."""

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    append_ledger(ledger_path, "event_received", event.to_dict())

    decision = route_event(event)
    append_ledger(ledger_path, "route_decision", decision.to_dict())

    actions = plan_actions(event, decision)
    results: list[ActionResult] = []
    for action in actions:
        append_ledger(ledger_path, "action_planned", action.to_dict())
        result = execute_action(action, dry_run=dry_run)
        results.append(result)
        append_ledger(ledger_path, "action_result", result.to_dict())

    return {
        "event": event.to_dict(),
        "decision": decision.to_dict(),
        "actions": [action.to_dict() for action in actions],
        "results": [result.to_dict() for result in results],
        "ledger": str(ledger_path),
    }


def append_ledger(path: Path, kind: str, payload: dict[str, Any]) -> None:
    """Append one JSONL ledger record."""

    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "payload": payload,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def read_ledger(path: Path) -> list[dict[str, Any]]:
    """Read JSONL ledger records."""

    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _stable_id(*parts: str) -> str:
    raw = "\0".join(parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
    return f"{parts[0]}:{parts[1]}:{digest}"


def _subject_from_link(link: str, repo: str, connector: str) -> EventSubject:
    number = ""
    subject_type = "github.repo"
    issue_match = re.search(r"/issues/(\d+)", link or "")
    pull_match = re.search(r"/pull/(\d+)", link or "")
    if issue_match:
        number = issue_match.group(1)
        subject_type = "github.issue"
    elif pull_match:
        number = pull_match.group(1)
        subject_type = "github.pull"
    elif connector == "comments":
        subject_type = "github.thread"
    return EventSubject(type=subject_type, repo=repo, number=number)


def _matches_rule(event: TriggerEvent, rule: Rule) -> bool:
    for field_name, expected in rule.match.items():
        actual = _event_field(event, field_name)
        if isinstance(expected, (list, tuple, set)):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _event_field(event: TriggerEvent, dotted: str) -> Any:
    value: Any = event
    for part in dotted.split("."):
        if hasattr(value, part):
            value = getattr(value, part)
        elif isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def _action_job(
    event: TriggerEvent,
    action_type: str,
    mode: str,
    *,
    target: dict[str, Any] | None = None,
    input: dict[str, Any] | None = None,
    requires_approval: bool = False,
) -> ActionJob:
    action_id = _stable_id("action", action_type, event.event_id)
    return ActionJob(
        action_id=action_id,
        event_id=event.event_id,
        type=action_type,
        mode=mode,
        target=target or {},
        input=input or {},
        idempotency_key=f"{action_type}:{event.event_id}:v1",
        requires_approval=requires_approval,
    )
