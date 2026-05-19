"""Tests for feed.py — RSS/Atom parsing and URL generation."""

import pytest
from chatrss.feed import parse_rss, github_feed_urls, FeedItem

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>leanprover/lean-eval Issues</title>
    <link>https://github.com/leanprover/lean-eval/issues</link>
    <item>
      <title>Extractor mis-handles open…in inside definitions</title>
      <link>https://github.com/leanprover/lean-eval/issues/277</link>
      <guid>https://github.com/leanprover/lean-eval/issues/277</guid>
      <pubDate>Mon, 19 May 2026 10:00:00 +0000</pubDate>
      <description>Bug description here</description>
    </item>
    <item>
      <title>Extractor drops variable binders</title>
      <link>https://github.com/leanprover/lean-eval/issues/276</link>
      <guid>https://github.com/leanprover/lean-eval/issues/276</guid>
      <pubDate>Mon, 19 May 2026 09:00:00 +0000</pubDate>
      <description>Another bug</description>
    </item>
  </channel>
</rss>"""

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>leanprover/lean-eval Pull Requests</title>
  <entry>
    <id>https://github.com/leanprover/lean-eval/pull/280</id>
    <title>fix: emit variable declarations</title>
    <link href="https://github.com/leanprover/lean-eval/pull/280"/>
    <updated>2026-05-19T10:00:00Z</updated>
    <summary>Fix for variable declarations</summary>
  </entry>
</feed>"""


class TestParseRss:
    def test_rss_items_count(self):
        items = parse_rss(SAMPLE_RSS, "issue")
        assert len(items) == 2

    def test_rss_item_fields(self):
        items = parse_rss(SAMPLE_RSS, "issue")
        item = items[0]
        assert "277" in item.guid
        assert "Extractor" in item.title
        assert item.source == "issue"
        assert "github.com" in item.link

    def test_atom_items(self):
        items = parse_rss(SAMPLE_ATOM, "pull")
        assert len(items) == 1
        item = items[0]
        assert "280" in item.guid
        assert "variable" in item.title
        assert item.source == "pull"

    def test_empty_xml(self):
        items = parse_rss("", "issue")
        assert items == []

    def test_invalid_xml(self):
        items = parse_rss("not xml at all", "issue")
        assert items == []


class TestGithubFeedUrls:
    def test_default_urls(self):
        urls = github_feed_urls("leanprover", "lean-eval")
        assert "issue" in urls
        assert "pull" in urls
        assert "repo_event" in urls
        assert "comments" in urls
        assert "leanprover/lean-eval" in urls["issue"]
        assert "localhost:1200" in urls["issue"]

    def test_custom_rsshub_url(self):
        urls = github_feed_urls("owner", "repo", rsshub_url="https://my-rsshub.com")
        assert urls["issue"].startswith("https://my-rsshub.com")

    def test_trailing_slash_stripped(self):
        urls = github_feed_urls("a", "b", rsshub_url="http://localhost:1200/")
        assert not urls["issue"].startswith("http://localhost:1200//")
