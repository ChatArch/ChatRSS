"""RSSHub 服务管理：封装 docker-compose 操作。

chatrss server start    启动 RSSHub 容器
chatrss server stop     停止容器
chatrss server restart  重启容器
chatrss server status   查看运行状态
chatrss server logs     查看容器日志
chatrss server url      打印当前 RSSHub 地址
"""

from __future__ import annotations

import importlib.resources
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


# ── docker-compose 文件路径 ────────────────────────────────────────────────────

def _compose_file() -> Path:
    """
    解析内置 docker-compose.yml 的路径。
    优先使用 ~/.chatarch/chatrss/docker-compose.yml（用户可自定义覆盖），
    否则使用 package 内置的版本。
    """
    user_file = Path.home() / ".chatarch" / "chatrss" / "docker-compose.yml"
    if user_file.exists():
        return user_file
    # 从 package resources 导出到临时位置（importlib.resources 保证包内可用）
    ref = importlib.resources.files("chatrss.resources").joinpath("docker-compose.yml")
    with importlib.resources.as_file(ref) as p:
        return Path(p)


def _compose_dir() -> Path:
    """docker-compose 的工作目录（决定容器前缀名）。"""
    d = Path.home() / ".chatarch" / "chatrss"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ensure_compose_file() -> Path:
    """确保用户目录里有 docker-compose.yml，返回路径。"""
    target = _compose_dir() / "docker-compose.yml"
    if not target.exists():
        ref = importlib.resources.files("chatrss.resources").joinpath("docker-compose.yml")
        with importlib.resources.as_file(ref) as src:
            shutil.copy(src, target)
    return target


def _run_compose(args: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    """在 chatrss compose 工作目录运行 docker-compose 命令。"""
    compose_file = _ensure_compose_file()
    cmd = ["docker-compose", "-f", str(compose_file)] + args
    return subprocess.run(
        cmd,
        cwd=str(_compose_dir()),
        capture_output=capture,
        text=True,
    )


# ── 公开 API ──────────────────────────────────────────────────────────────────

def start(port: int = 1200) -> int:
    env = os.environ.copy()
    env["RSSHUB_PORT"] = str(port)
    compose_file = _ensure_compose_file()
    result = subprocess.run(
        ["docker-compose", "-f", str(compose_file), "up", "-d"],
        cwd=str(_compose_dir()),
        env=env,
        text=True,
    )
    return result.returncode


def stop() -> int:
    return _run_compose(["down"]).returncode


def restart() -> int:
    return _run_compose(["restart"]).returncode


def status() -> str:
    result = _run_compose(["ps"], capture=True)
    return result.stdout or result.stderr


def logs(lines: int = 50) -> str:
    result = _run_compose(["logs", "--tail", str(lines)], capture=True)
    return result.stdout or result.stderr


def is_running(port: int = 1200) -> bool:
    """检查 RSSHub 是否在指定端口响应。"""
    import httpx
    try:
        r = httpx.get(f"http://localhost:{port}/healthz", timeout=3)
        return r.status_code == 200 and r.text.strip() == "ok"
    except Exception:
        return False


def get_url(port: int = 1200) -> str:
    return f"http://localhost:{port}"
