"""Tests for watcher.py — seen dedup and event detection."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from chatrss.feed import FeedItem
from chatrss.watcher import SeenSet, _is_new, _append_jsonl, jsonl_path


def _make_item(guid: str, source: str = "issue") -> FeedItem:
    return FeedItem(
        guid=guid, title=f"Title {guid}", link=f"https://example.com/{guid}",
        description="", pub_date="2026-05-19", source=source,
    )


class TestSeenSet:
    def test_empty_seen(self, tmp_path):
        p = tmp_path / "test.seen"
        seen = SeenSet(p)
        assert not seen.contains("abc")

    def test_add_and_persist(self, tmp_path):
        p = tmp_path / "test.seen"
        seen = SeenSet(p)
        seen.add("guid1")
        seen.add("guid2")
        seen.save()

        seen2 = SeenSet(p)
        assert seen2.contains("guid1")
        assert seen2.contains("guid2")
        assert not seen2.contains("guid3")

    def test_load_existing(self, tmp_path):
        p = tmp_path / "test.seen"
        p.write_text(json.dumps({"guids": ["a", "b"]}))
        seen = SeenSet(p)
        assert seen.contains("a")
        assert seen.contains("b")


class TestIsNew:
    def test_new_item(self, tmp_path):
        seen = SeenSet(tmp_path / "test.seen")
        item = _make_item("guid-new")
        assert _is_new(item, seen)

    def test_already_seen(self, tmp_path):
        seen = SeenSet(tmp_path / "test.seen")
        seen.add("guid-old")
        item = _make_item("guid-old")
        assert not _is_new(item, seen)


class TestAppendJsonl:
    def test_appends_items(self, tmp_path):
        with patch("chatrss.watcher._state_dir", return_value=tmp_path):
            items = [_make_item("g1"), _make_item("g2", "pull")]
            _append_jsonl("owner/repo", items)
            p = tmp_path / "owner__repo.jsonl"
            lines = p.read_text().strip().splitlines()
            assert len(lines) == 2
            d = json.loads(lines[0])
            assert d["guid"] == "g1"
            assert d["source"] == "issue"

    def test_empty_list_no_file(self, tmp_path):
        with patch("chatrss.watcher._state_dir", return_value=tmp_path):
            _append_jsonl("owner/repo", [])
            p = tmp_path / "owner__repo.jsonl"
            assert not p.exists()
