"""RSS/Atom feed 拉取与解析。

chatrss 不调用 GitHub API，而是消费 RSSHub 提供的 feed。
RSSHub GitHub 路由参考：
  /github/issue/:user/:repo/:state?     - Issues
  /github/pull/:user/:repo/:state?      - Pull Requests
  /github/repo_event/:owner/:repo       - Repo Events（push/star/fork/...）
  /github/comments/:user/:repo/:number? - Comments
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

import httpx


# ── Feed URL 模板 ──────────────────────────────────────────────────────────────

def github_feed_urls(owner: str, repo: str, rsshub_url: str = "http://localhost:1200") -> dict[str, str]:
    """生成 GitHub 仓库的标准 RSSHub feed URL 集合。"""
    base = rsshub_url.rstrip("/")
    return {
        "issue":      f"{base}/github/issue/{owner}/{repo}/open",
        "pull":       f"{base}/github/pull/{owner}/{repo}/open",
        "repo_event": f"{base}/github/repo_event/{owner}/{repo}",
        "comments":   f"{base}/github/comments/{owner}/{repo}",
    }


# ── 解析结构 ──────────────────────────────────────────────────────────────────

@dataclass
class FeedItem:
    guid: str           # 唯一 ID（来自 <guid> 或 <id> 或 link）
    title: str
    link: str
    description: str    # 原始 HTML/text 内容
    pub_date: str       # 字符串，保留原始值
    source: str         # feed 类型（issue/pull/repo_event/...）


# ── RSS/Atom 解析 ─────────────────────────────────────────────────────────────

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def _text(el, tag: str, default: str = "") -> str:
    child = el.find(tag)
    return (child.text or default) if child is not None else default


def parse_rss(xml_text: str, source: str) -> list[FeedItem]:
    """解析 RSS 2.0 或 Atom feed，返回 FeedItem 列表。"""
    items: list[FeedItem] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    tag = root.tag.lower()

    # Atom
    if "atom" in tag or root.tag == "{http://www.w3.org/2005/Atom}feed":
        ns = "http://www.w3.org/2005/Atom"
        for entry in root.findall(f"{{{ns}}}entry"):
            link_el = entry.find(f"{{{ns}}}link")
            link = link_el.get("href", "") if link_el is not None else ""
            guid_el = entry.find(f"{{{ns}}}id")
            guid = guid_el.text or link if guid_el is not None else link
            summary_el = entry.find(f"{{{ns}}}summary")
            content_el = entry.find(f"{{{ns}}}content")
            desc = ""
            if content_el is not None:
                desc = content_el.text or ""
            elif summary_el is not None:
                desc = summary_el.text or ""
            updated_el = entry.find(f"{{{ns}}}updated")
            if updated_el is None:
                updated_el = entry.find(f"{{{ns}}}published")
            items.append(FeedItem(
                guid=guid,
                title=(_text(entry, f"{{{ns}}}title") or "").strip(),
                link=link,
                description=desc,
                pub_date=updated_el.text if updated_el is not None else "",
                source=source,
            ))
        return items

    # RSS 2.0
    channel = root.find("channel")
    if channel is None:
        channel = root
    for item in channel.findall("item"):
        guid_el = item.find("guid")
        link = _text(item, "link")
        guid = (guid_el.text or link) if guid_el is not None else link
        content_el = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
        desc = (content_el.text or "") if content_el is not None else _text(item, "description")
        items.append(FeedItem(
            guid=guid,
            title=_text(item, "title").strip(),
            link=link,
            description=desc,
            pub_date=_text(item, "pubDate"),
            source=source,
        ))
    return items


# ── HTTP 拉取 ─────────────────────────────────────────────────────────────────

def fetch_feed(url: str, client: Optional[httpx.Client] = None) -> list[FeedItem]:
    """拉取单个 feed URL，返回解析后的 FeedItem 列表。"""
    source = _infer_source(url)
    close = False
    if client is None:
        client = httpx.Client(timeout=15, follow_redirects=True)
        close = True
    try:
        resp = client.get(url, headers={"User-Agent": "chatrss/1.0"})
        resp.raise_for_status()
        return parse_rss(resp.text, source)
    finally:
        if close:
            client.close()


def fetch_feeds(urls: dict[str, str]) -> list[FeedItem]:
    """批量拉取多个 feed，返回合并后的 FeedItem 列表。"""
    items: list[FeedItem] = []
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        for source, url in urls.items():
            try:
                fetched = fetch_feed(url, client)
                items.extend(fetched)
            except Exception:
                pass
    return items


def _infer_source(url: str) -> str:
    """从 URL 推断 feed 类型。"""
    for keyword in ("issue", "pull", "repo_event", "comments", "discussion"):
        if keyword in url:
            return keyword
    return "unknown"
