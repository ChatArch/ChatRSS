"""Tests for task-oriented action handling."""

from chatrss.actions import format_message, process_items, send_messages
from chatrss.feed import FeedItem


def _make_item(source: str, guid: str = "1") -> FeedItem:
    return FeedItem(
        guid=guid,
        title=f"Title {guid}",
        link=f"https://github.com/owner/repo/{source}/{guid}",
        description="",
        pub_date="Mon, 19 May 2026 10:00:00 +0000",
        source=source,
    )


def test_format_message_includes_task_action():
    text = format_message(_make_item("issue"), "owner/repo")

    assert "[Issue 任务]" in text
    assert "处理：" in text
    assert "先" in text


def test_comments_are_task_notifications(monkeypatch):
    calls = []

    def fake_run_lark(args):
        calls.append(args)
        return 0, "", ""

    monkeypatch.setattr("chatrss.actions._run_lark", fake_run_lark)

    sent = send_messages([_make_item("comments")], "owner/repo", "ou_user")

    assert sent == 1
    assert calls
    assert "评论任务" in calls[0][-1]


def test_repo_events_are_background_only(monkeypatch):
    calls = []

    def fake_run_lark(args):
        calls.append(args)
        return 0, "", ""

    monkeypatch.setattr("chatrss.actions._run_lark", fake_run_lark)

    sent = send_messages([_make_item("repo_event")], "owner/repo", "ou_user")

    assert sent == 0
    assert calls == []


def test_process_items_counts_tasks_and_background():
    stats = process_items(
        [_make_item("issue"), _make_item("pull"), _make_item("comments"), _make_item("repo_event")],
        "owner/repo",
    )

    assert stats["tasks"] == 3
    assert stats["skipped"] == 1
    assert stats["messages_sent"] == 0
    assert stats["doc_rows_added"] == 0
