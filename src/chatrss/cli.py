"""CLI entrypoint for chatrss."""

from __future__ import annotations

import json
import sys
import time

import click
from chatstyle import render_success, render_warning

from chatrss.config import ChatRssConfig


def _load_config():
    from chatenv import get_paths
    ChatRssConfig.load_all(get_paths().envs_dir)
    return ChatRssConfig


def _resolve_repo(repo: str | None) -> str:
    cfg = _load_config()
    if repo:
        return repo.strip()
    default = cfg.CHATRSS_DEFAULT_REPO.value
    if default:
        return default
    raise click.UsageError(
        "缺少 REPO。传入 owner/name 或执行 `chatenv init -t chatrss`。"
    )


def _resolve_rsshub(rsshub_url: str | None) -> str:
    cfg = _load_config()
    return rsshub_url or cfg.CHATRSS_RSSHUB_URL.value or "http://localhost:1200"


@click.group()
def main() -> None:
    """chatrss — RSSHub feed 监听 + 飞书联动。"""


# ── init ──────────────────────────────────────────────────────────────────────

@main.command("init")
@click.argument("repo", required=False)
@click.option("--rsshub-url", default=None, envvar="CHATRSS_RSSHUB_URL")
def cmd_init(repo: str | None, rsshub_url: str | None) -> None:
    """初始化 seen 状态，避免首次运行重放历史条目。

    REPO: owner/name，如 leanprover/lean-eval
    """
    from chatrss.watcher import init_seen, seen_path

    r = _resolve_repo(repo)
    url = _resolve_rsshub(rsshub_url)
    click.echo(f"初始化：{r}（RSSHub: {url}）...")
    try:
        n = init_seen(r, url)
        render_success(f"已标记 {n} 条历史条目 → {seen_path(r)}")
    except Exception as exc:
        click.echo(f"失败：{exc}", err=True)
        sys.exit(1)


# ── watch ─────────────────────────────────────────────────────────────────────

@main.command("watch")
@click.argument("repo", required=False)
@click.option("--interval", default=300, type=int, show_default=True)
@click.option("--rsshub-url", default=None, envvar="CHATRSS_RSSHUB_URL")
@click.option("--feeds", default=None, help="逗号分隔的 feed 类型：issue,pull,repo_event,comments")
@click.option("--doc", default=None, envvar="CHATRSS_LARK_DOC_TOKEN")
@click.option("--notify-user", default=None, envvar="CHATRSS_LARK_USER_ID")
@click.option("--once", is_flag=True, help="只轮询一次（调试用）")
def cmd_watch(repo: str | None, interval: int, rsshub_url: str | None,
              feeds: str | None, doc: str | None,
              notify_user: str | None, once: bool) -> None:
    """监听仓库 RSS feed，发现新条目时通知飞书 + 更新文档。

    REPO: owner/name，如 leanprover/lean-eval
    """
    from chatrss.watcher import poll_once, seen_path
    from chatrss.actions import process_items

    r = _resolve_repo(repo)
    url = _resolve_rsshub(rsshub_url)
    cfg = _load_config()
    effective_doc = doc or cfg.CHATRSS_LARK_DOC_TOKEN.value
    effective_user = notify_user or cfg.CHATRSS_LARK_USER_ID.value
    feed_list = [f.strip() for f in feeds.split(",")] if feeds else None

    if not seen_path(r).exists():
        render_warning(f"未初始化，建议先运行：chatrss init {r}")

    click.echo(f"监听：{r}")
    click.echo(f"  RSSHub:   {url}")
    click.echo(f"  feeds:    {feeds or 'issue,pull,repo_event,comments'}")
    click.echo(f"  间隔:     {interval}s")
    click.echo(f"  文档:     {effective_doc or '未配置'}")
    click.echo(f"  通知:     {effective_user or '未配置'}")
    click.echo()

    round_n = 0
    while True:
        round_n += 1
        try:
            items = poll_once(r, url, feed_list)
        except Exception as exc:
            click.echo(f"[{round_n}] 轮询出错：{exc}", err=True)
            if once:
                sys.exit(1)
            time.sleep(interval)
            continue

        if items:
            click.echo(f"[{round_n}] 发现 {len(items)} 条新事件：")
            for it in items:
                click.echo(f"  [{it.source}] {it.title[:60]}")
            stats = process_items(items, r, effective_user, effective_doc)
            click.echo(f"  → 消息 {stats['messages_sent']} 条，文档 +{stats['doc_rows_added']} 行")
        else:
            click.echo(f"[{round_n}] 无新事件")

        if once:
            break
        time.sleep(interval)


# ── cat ───────────────────────────────────────────────────────────────────────

@main.command("cat")
@click.argument("repo", required=False)
@click.option("--limit", default=20, type=int, show_default=True)
@click.option("--json-output", is_flag=True)
def cmd_cat(repo: str | None, limit: int, json_output: bool) -> None:
    """查看本地事件日志（只读，不访问网络）。"""
    from chatrss.watcher import read_jsonl, jsonl_path

    r = _resolve_repo(repo)
    events = read_jsonl(r)
    if not events:
        click.echo(f"暂无事件日志：{jsonl_path(r)}")
        return

    recent = events[-limit:]
    if json_output:
        click.echo(json.dumps(recent, ensure_ascii=False, indent=2))
        return

    click.echo(f"{jsonl_path(r)}（共 {len(events)} 条，显示最近 {len(recent)} 条）\n")
    for ev in recent:
        click.echo(f"  [{ev.get('source')}] {ev.get('title','')[:60]}")
        click.echo(f"    {ev.get('pub_date','')} | {ev.get('link','')}")


if __name__ == "__main__":
    main()
