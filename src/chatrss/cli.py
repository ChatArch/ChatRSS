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


# ── server 命令组 ──────────────────────────────────────────────────────────────

@main.group("server")
def server_group() -> None:
    """管理本地 RSSHub 服务（基于 docker-compose）。"""


@server_group.command("start")
@click.option("--port", default=1200, type=int, show_default=True, help="监听端口")
def server_start(port: int) -> None:
    """启动 RSSHub 容器。"""
    from chatrss.server import start, is_running, get_url

    if is_running(port):
        render_warning(f"RSSHub 已在运行：{get_url(port)}")
        return
    click.echo("启动 RSSHub...")
    code = start(port)
    if code == 0:
        render_success(f"RSSHub 已启动：{get_url(port)}")
    else:
        click.echo("启动失败，请检查 docker-compose 输出", err=True)
        sys.exit(code)


@server_group.command("stop")
def server_stop() -> None:
    """停止 RSSHub 容器。"""
    from chatrss.server import stop

    click.echo("停止 RSSHub...")
    code = stop()
    if code == 0:
        render_success("RSSHub 已停止")
    else:
        click.echo("停止失败", err=True)


@server_group.command("restart")
def server_restart() -> None:
    """重启 RSSHub 容器。"""
    from chatrss.server import restart

    click.echo("重启 RSSHub...")
    code = restart()
    if code == 0:
        render_success("RSSHub 已重启")
    else:
        click.echo("重启失败", err=True)


@server_group.command("status")
def server_status() -> None:
    """查看 RSSHub 容器状态。"""
    from chatrss.server import status, is_running

    click.echo(status())
    health = "✅ 响应正常" if is_running() else "❌ 未响应"
    click.echo(f"\nhealth: {health}")


@server_group.command("logs")
@click.option("--tail", default=50, type=int, show_default=True)
def server_logs(tail: int) -> None:
    """查看 RSSHub 容器日志。"""
    from chatrss.server import logs

    click.echo(logs(tail))


@server_group.command("url")
def server_url() -> None:
    """打印当前 RSSHub 地址。"""
    from chatrss.server import get_url, is_running
    url = get_url()
    status = "✅" if is_running() else "❌ 未运行"
    click.echo(f"{url}  {status}")


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

    click.echo(f"监听：{r}")
    click.echo(f"  RSSHub:   {url}")
    click.echo(f"  feeds:    {feeds or 'issue,pull,repo_event,comments'}")
    click.echo(f"  间隔:     {interval}s")
    click.echo(f"  文档:     {effective_doc or '未配置'}")
    click.echo(f"  通知:     {effective_user or '未配置'}")
    click.echo(f"  策略:     启动时静默同步，只通知 watch 运行期间的新 issue/PR")
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


@main.command("ps")
def cmd_ps() -> None:
    """查看当前正在运行的 chatrss watch 进程。"""
    import subprocess as _sp
    result = _sp.run(
        ["pgrep", "-af", "chatrss watch"],
        capture_output=True, text=True,
    )
    lines = [l for l in result.stdout.splitlines() if "pgrep" not in l and l.strip()]
    if not lines:
        click.echo("没有正在运行的 chatrss watch 进程。")
        return
    click.echo(f"运行中的 watch 进程（{len(lines)} 个）：\n")
    for line in lines:
        # 解析 pid 和参数
        parts = line.split(None, 1)
        pid = parts[0]
        cmd = parts[1] if len(parts) > 1 else ""
        # 提取 repo（第一个非 --flag 的参数）
        import re as _re
        repo_m = _re.search(r'watch\s+([^\s-][^\s]*)', cmd)
        repo = repo_m.group(1) if repo_m else "?"
        click.echo(f"  pid {pid}  repo: {repo}")
        click.echo(f"    {cmd[:120]}")


if __name__ == "__main__":
    main()
