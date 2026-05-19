"""事件触发动作：飞书消息通知 + 飞书文档更新。"""

from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone
from typing import Optional

from chatrss.feed import FeedItem


def _now_cn() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")


def _run_lark(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(["lark-cli"] + args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


# ── 消息格式 ──────────────────────────────────────────────────────────────────

_SOURCE_EMOJI = {
    "issue":      "🐛",
    "pull":       "🔀",
    "repo_event": "📦",
    "comments":   "💬",
}

_SOURCE_LABEL = {
    "issue":      "新 Issue",
    "pull":       "新 PR",
    "repo_event": "仓库事件",
    "comments":   "新评论",
}


def format_message(item: FeedItem, repo: str) -> str:
    emoji = _SOURCE_EMOJI.get(item.source, "📌")
    label = _SOURCE_LABEL.get(item.source, item.source)
    lines = [
        f"{emoji} [{label}] {repo}",
        f"标题：{item.title}",
        f"链接：{item.link}",
    ]
    if item.pub_date:
        lines.append(f"时间：{item.pub_date[:19]}")
    return "\n".join(lines)


def send_message(item: FeedItem, repo: str, user_id: str) -> bool:
    text = format_message(item, repo)
    code, _, _ = _run_lark([
        "im", "+messages-send",
        "--user-id", user_id,
        "--text", text,
    ])
    return code == 0


def send_messages(items: list[FeedItem], repo: str, user_id: str) -> int:
    ok = 0
    for item in items:
        if send_message(item, repo, user_id):
            ok += 1
    return ok


# ── 文档更新 ──────────────────────────────────────────────────────────────────

def append_to_doc(items: list[FeedItem], repo: str, doc_token: str) -> int:
    """将新条目追加到飞书文档的事件日志表格。"""
    if not items:
        return 0

    rows = []
    ts = _now_cn()
    for item in items:
        label = _SOURCE_LABEL.get(item.source, item.source)
        title = item.title[:60]
        rows.append(
            f'<tr>'
            f'<td><p>{ts}</p></td>'
            f'<td><p>{label}</p></td>'
            f'<td><p><a href="{item.link}">{title}</a></p></td>'
            f'<td><p>{item.pub_date[:10] if item.pub_date else ""}</p></td>'
            f'</tr>'
        )

    content = "\n".join(rows)
    code, _, _ = _run_lark([
        "docs", "+update",
        "--api-version", "v2",
        "--doc", doc_token,
        "--command", "append",
        "--content", content,
    ])
    return len(items) if code == 0 else 0


def process_items(
    items: list[FeedItem],
    repo: str,
    user_id: Optional[str] = None,
    doc_token: Optional[str] = None,
) -> dict:
    """统一处理新条目：发消息 + 更新文档。"""
    stats = {"messages_sent": 0, "doc_rows_added": 0}
    if not items:
        return stats
    if user_id:
        stats["messages_sent"] = send_messages(items, repo, user_id)
    if doc_token:
        stats["doc_rows_added"] = append_to_doc(items, repo, doc_token)
    return stats
