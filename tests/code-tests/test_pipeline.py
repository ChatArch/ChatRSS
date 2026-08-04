"""Tests for the trigger-router-action MVP pipeline."""

import json

from chatrss.events import EventSubject, TriggerEvent
from chatrss.feed import FeedItem
from chatrss.pipeline import (
    event_from_feed_item,
    plan_actions,
    read_ledger,
    route_event,
    run_event_flow,
    sample_multi_agent_event,
)


def test_comment_event_routes_to_agent_and_draft_comment():
    event = sample_multi_agent_event()

    decision = route_event(event)
    actions = plan_actions(event, decision)

    assert decision.decision == "act"
    assert "agent.run" in decision.action_hints
    assert "github.comment.draft" in decision.action_hints
    assert {action.type for action in actions} == {"internal.notify", "agent.run", "github.comment"}
    assert [action for action in actions if action.type == "github.comment"][0].requires_approval


def test_repo_event_is_archived_without_actions():
    event = TriggerEvent(
        event_id="demo:repo-event",
        source="rsshub",
        connector="repo_event",
        event_type="github.repo_event.item",
        title="push to main",
        url="https://github.com/ChatArch/ChatRSS",
        subject=EventSubject(type="github.repo", repo="ChatArch/ChatRSS"),
    )

    decision = route_event(event)

    assert decision.decision == "archive"
    assert plan_actions(event, decision) == []


def test_feed_item_can_be_normalized_to_event():
    item = FeedItem(
        guid="https://github.com/ChatArch/ChatRSS/issues/12#issuecomment-456",
        title="New comment on issue 12",
        link="https://github.com/ChatArch/ChatRSS/issues/12#issuecomment-456",
        description="请检查这个信号",
        pub_date="2026-08-05T10:00:00Z",
        source="comments",
    )

    event = event_from_feed_item(item, "ChatArch/ChatRSS")

    assert event.source == "rsshub"
    assert event.connector == "comments"
    assert event.subject.repo == "ChatArch/ChatRSS"
    assert event.subject.number == "12"
    assert event.event_id.startswith("rsshub:comments:")


def test_run_event_flow_writes_ledger(tmp_path):
    ledger = tmp_path / "flow.ledger.jsonl"

    result = run_event_flow(sample_multi_agent_event(), ledger)
    records = read_ledger(ledger)

    assert result["decision"]["decision"] == "act"
    assert [record["kind"] for record in records] == [
        "event_received",
        "route_decision",
        "action_planned",
        "action_result",
        "action_planned",
        "action_result",
        "action_planned",
        "action_result",
    ]
    assert all(json.dumps(record, ensure_ascii=False) for record in records)
    assert all(action_result["status"] == "DRY_RUN_OK" for action_result in result["results"])
