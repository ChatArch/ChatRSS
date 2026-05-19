"""GitHub 仓库 RSS 监听与 seen 去重。

核心流程：
1. 通过 RSSHub feed 拉取最新条目（不直接调 GitHub API）
2. 与本地 seen 状态比对，提取新条目
3. 新条目落盘 JSONL，返回给上层处理
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from chatrss.feed import FeedItem, fetch_feeds, github_feed_urls


# ── 状态目录 ──────────────────────────────────────────────────────────────────

def _state_dir() -> Path:
    base = Path(os.environ.get("CHATARCH_HOME", Path.home() / ".chatarch"))
    d = base / "chatrss"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _slug(repo: str) -> str:
    return repo.replace("/", "__")


def seen_path(repo: str) -> Path:
    return _state_dir() / f"{_slug(repo)}.seen"


def jsonl_path(repo: str) -> Path:
    return _state_dir() / f"{_slug(repo)}.jsonl"


# ── Seen 状态 ─────────────────────────────────────────────────────────────────

class SeenSet:
    """已处理条目的 GUID 集合，持久化为 JSON 文件。"""

    def __init__(self, path: Path):
        self._path = path
        self._guids: set[str] = set()
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self._guids = set(data.get("guids", []))

    def contains(self, guid: str) -> bool:
        return guid in self._guids

    def add(self, guid: str) -> None:
        self._guids.add(guid)

    def save(self) -> None:
        self._path.write_text(
            json.dumps({"guids": sorted(self._guids)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, repo: str) -> "SeenSet":
        return cls(seen_path(repo))


# ── 新事件检测 ────────────────────────────────────────────────────────────────

def _is_new(item: FeedItem, seen: SeenSet) -> bool:
    return not seen.contains(item.guid)


def _append_jsonl(repo: str, items: list[FeedItem]) -> None:
    if not items:
        return
    p = jsonl_path(repo)
    with p.open("a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")


# ── 公开 API ──────────────────────────────────────────────────────────────────

def init_seen(repo: str, rsshub_url: str = "http://localhost:1200") -> int:
    """初始化 seen 状态：拉取当前 feed，标记所有条目为已见。

    避免首次运行时把历史条目全部当作新事件处理。
    """
    owner, name = repo.split("/", 1)
    urls = github_feed_urls(owner, name, rsshub_url)
    items = fetch_feeds(urls)
    seen = SeenSet(seen_path(repo))
    for item in items:
        seen.add(item.guid)
    seen.save()
    return len(items)


def poll_once(repo: str, rsshub_url: str = "http://localhost:1200",
              feeds: Optional[list[str]] = None,
              silent: bool = False) -> list[FeedItem]:
    """轮询一次，返回新条目列表，并更新 seen + JSONL。

    Args:
        repo: owner/name
        rsshub_url: RSSHub 实例地址
        feeds: 指定拉取的 feed 类型列表（如 ["issue", "pull"]），默认全部
        silent: 静默模式——更新 seen 状态但不返回新条目也不落盘（用于启动时同步）
    """
    owner, name = repo.split("/", 1)
    all_urls = github_feed_urls(owner, name, rsshub_url)
    urls = {k: v for k, v in all_urls.items() if feeds is None or k in feeds}

    items = fetch_feeds(urls)
    seen = SeenSet.load(repo)

    new_items = [item for item in items if _is_new(item, seen)]
    for item in new_items:
        seen.add(item.guid)
    seen.save()

    if silent:
        return []   # 静默模式：seen 已更新，但不触发任何动作

    _append_jsonl(repo, new_items)
    return new_items


def watch(repo: str, interval: int = 300,
          rsshub_url: str = "http://localhost:1200",
          feeds: Optional[list[str]] = None) -> Iterator[list[FeedItem]]:
    """持续轮询，每次 yield 新条目列表（含空列表）。

    启动时自动执行一次静默同步，把当前 feed 状态全部标记为已见，
    之后只有 watch 运行期间出现的新条目才会触发动作。
    """
    # 启动时静默同步：标记当前所有条目为已见，不触发任何通知
    poll_once(repo, rsshub_url, feeds, silent=True)

    while True:
        items = poll_once(repo, rsshub_url, feeds)
        yield items
        time.sleep(interval)


def read_jsonl(repo: str) -> list[dict]:
    """读取本地 JSONL 事件日志。"""
    p = jsonl_path(repo)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
