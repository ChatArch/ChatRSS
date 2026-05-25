"""事件触发动作：飞书消息通知 + 飞书文档更新。

处理策略：
- 任务导向：issue / PR / comments 都视为需要处理的任务事件
- 先完成：通知文案优先给出下一步动作，不先抽象封装流程
- 后封装：repo_event 仅作为背景上下文落盘 JSONL，不打扰、不写文档

文档策略：
- 任务事件追加到事件日志表格末尾（用 block_insert_after 插到表末尾）
- repo_event 仅落盘 JSONL
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Optional

from chatrss.feed import FeedItem


def _now_cn() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")


def _parse_pub_date(raw: str) -> str:
    """RSS 日期字符串 → 北京时间 YYYY-MM-DD HH:MM。"""
    if not raw:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
        return (dt.astimezone(timezone(timedelta(hours=8)))).strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    try:
        from dateutil import parser as du
        dt = du.parse(raw)
        return (dt.astimezone(timezone(timedelta(hours=8)))).strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    return raw[:16]


def _run_lark(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(["lark-cli"] + args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


# ── 飞书消息（任务事件通知）────────────────────────────────────────────────────

_SOURCE_EMOJI = {"issue": "🐛", "pull": "🔀", "comments": "💬"}
_SOURCE_LABEL = {"issue": "Issue 任务", "pull": "PR 任务",
                 "repo_event": "仓库事件", "comments": "评论任务"}
_TASK_ACTION = {
    "issue": "先判断是否需要修复/回复；能直接处理就先完成。",
    "pull": "先完成审阅/合并/反馈；之后再考虑是否沉淀流程。",
    "comments": "先判断评论是否需要回复或代码改动；需要就立即处理。",
}


def _is_task_item(item: FeedItem) -> bool:
    """需要进入处理流的事件；repo_event 只做背景记录。"""
    return item.source in ("issue", "pull", "comments")


def _should_notify(item: FeedItem) -> bool:
    """需要主动打扰用户的任务事件。"""
    return _is_task_item(item)


def format_message(item: FeedItem, repo: str) -> str:
    emoji = _SOURCE_EMOJI.get(item.source, "📌")
    label = _SOURCE_LABEL.get(item.source, item.source)
    lines = [
        f"{emoji} [{label}] {repo}",
        f"标题：{item.title}",
        f"链接：{item.link}",
        f"处理：{_TASK_ACTION.get(item.source, '先完成当前处理，再看是否需要整理封装。')}",
    ]
    if item.pub_date:
        lines.append(f"时间：{_parse_pub_date(item.pub_date)}")
    return "\n".join(lines)


def send_messages(items: list[FeedItem], repo: str, user_id: str) -> int:
    """发送任务通知；背景事件忽略。"""
    ok = 0
    for item in items:
        if not _should_notify(item):
            continue
        text = format_message(item, repo)
        code, _, _ = _run_lark(["im", "+messages-send", "--user-id", user_id, "--text", text])
        if code == 0:
            ok += 1
    return ok


# ── 飞书文档（任务事件插入事件日志表格末尾）───────────────────────────────────

def _extract_number(link: str) -> str:
    m = re.search(r'/(\d+)$', link or "")
    return f"#{m.group(1)}" if m else "—"


def _build_table_row(item: FeedItem) -> str:
    """构建 5 列的表格行 XML：时间 | 事件类型 | 编号 | 标题 | 发布时间。"""
    ts = _now_cn()
    label = _SOURCE_LABEL.get(item.source, item.source)
    num = _extract_number(item.link)
    title = item.title[:60]
    pub = _parse_pub_date(item.pub_date)
    return (
        f'<tr>'
        f'<td><p>{ts}</p></td>'
        f'<td><p>{label}</p></td>'
        f'<td><p><a href="{item.link}">{num}</a></p></td>'
        f'<td><p>{title}</p></td>'
        f'<td><p>{pub}</p></td>'
        f'</tr>'
    )


def _get_last_row_block_id(doc_token: str) -> Optional[str]:
    """拉取事件日志表格，返回最后一个数据行的最后一个 <p> 的 block id。
    用来作为 block_insert_after 的锚点。
    """
    code, out, _ = _run_lark([
        "docs", "+fetch", "--api-version", "v2",
        "--doc", doc_token,
        "--scope", "keyword", "--keyword", "事件日志",
    ])
    if code != 0:
        return None
    import json
    try:
        content = json.loads(out)["data"]["document"]["content"]
    except Exception:
        return None
    # 找事件日志 table 内所有 <p id="..."> 的最后一个
    ids = re.findall(r'<p id="(doxcn[^"]+)">', content)
    # 跳过表头（第一行 5 个 th → 5 个 p），取最后一个数据行末尾的 p
    return ids[-1] if ids else None


def append_to_event_log(items: list[FeedItem], repo: str, doc_token: str) -> int:
    """将任务事件插入到飞书文档事件日志表格末尾。"""
    to_write = [item for item in items if _is_task_item(item)]
    if not to_write:
        return 0

    ok = 0
    for item in to_write:
        # 每次都重新拿最后一行，保证顺序正确
        last_id = _get_last_row_block_id(doc_token)
        if not last_id:
            continue
        row_xml = _build_table_row(item)
        code, _, _ = _run_lark([
            "docs", "+update", "--api-version", "v2",
            "--doc", doc_token,
            "--command", "block_insert_after",
            "--block-id", last_id,
            "--content", row_xml,
        ])
        if code == 0:
            ok += 1
    return ok


# ── 统一处理 ──────────────────────────────────────────────────────────────────

def process_items(
    items: list[FeedItem],
    repo: str,
    user_id: Optional[str] = None,
    doc_token: Optional[str] = None,
) -> dict:
    """处理新条目：任务事件通知/写文档，repo_event 仅计入背景统计。"""
    stats = {"messages_sent": 0, "doc_rows_added": 0, "tasks": 0, "skipped": 0}
    if not items:
        return stats

    stats["tasks"] = sum(1 for it in items if _is_task_item(it))
    stats["skipped"] = len(items) - stats["tasks"]

    if user_id:
        stats["messages_sent"] = send_messages(items, repo, user_id)
    if doc_token:
        stats["doc_rows_added"] = append_to_event_log(items, repo, doc_token)

    return stats
