<div align="center">
    <a href="https://pypi.python.org/pypi/chatrss">
        <img src="https://img.shields.io/pypi/v/chatrss.svg" alt="PyPI version" />
    </a>
    <a href="./.github/workflows/ci.yml">
        <img src="https://img.shields.io/badge/ci-github_actions-blue.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatRSS/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[英文版](README.en.md) | [简体中文](README.md)
</div>

# ChatRSS

ChatRSS 是 ChatArch 的 RSS / RSSHub-first trigger-router-action 工具：RSSHub 负责把外部世界变成 feed，ChatRSS 负责把 feed 和其他事件源变成可去重、可路由、可审计、可触发 Agent 的事件流。

文档站：<https://arch.gh.wzhecnu.cn/ChatRSS/>

## 现在能做什么

| 能力 | 当前状态 | 入口 |
| --- | --- | --- |
| RSSHub/GitHub feed 监听 | 已实现 | `chatrss watch` |
| 本地 RSSHub 容器辅助管理 | 已实现，需要本机 Docker / docker-compose | `chatrss server ...` |
| 本地事件日志查看 | 已实现 | `chatrss cat` |
| Trigger-Router-Action 本地闭环 | 已实现 dry-run MVP | `chatrss flow demo` |
| 真实 Zulip / Discourse / Mattermost trigger + 回帖案例 | 已在受控服务环境用统一 actor `RexWang` 验证 | [真实事件案例](docs/real-world-cases.md) / [Mattermost](docs/platforms/mattermost.md) |
| 多平台 trigger / router / action 框架 | 规划中，已有 schema 和 dry-run seam | [能力地图](docs/capability-map.md) |

## 快速开始

```bash
python -m pip install -e ".[dev,docs]"
chatrss --help
chatrss --tree
chatrss --version
chatrss flow demo --ledger ./playground/flow.ledger.jsonl --json-output
python -m pytest -q
mkdocs build --strict
```

如果本机没有全局 `chatrss`，可在源码目录用：

```bash
PYTHONPATH=src python -m chatrss.cli flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

## 文档入口

- [快速开始](docs/quickstart.md)：安装、demo、watch、RSSHub server 边界。
- [CLI 树](docs/cli-tree.md)：`chatrss --tree` 当前已实现命令树和 minor 目标命令树。
- [能力地图](docs/capability-map.md)：Trigger、Event、Router、Model、Action、Ledger 的状态和边界。
- [接口树](docs/interface-tree.md)：CLI 到 Python API / module 的映射。
- [Trigger-Router-Action 设计](docs/trigger-router-action.md)：架构和事件协议。
- [真实平台实践计划](docs/practice-plan.md)：Zulip、Discourse、Mattermost、Revolt、GitHub、Gitea 接入顺序。
- [真实事件案例](docs/real-world-cases.md)：Zulip、Discourse、Mattermost 的真实平台 trigger/action 闭环。
- [Zulip @mention 快速开始](docs/zulip-quickstart.md)：第一条真实平台 trigger 验证。

## Minor 版本方向

```text
Trigger Connector
  -> Event Schema / Inbox
  -> Rule Router
  -> Model Router
  -> Action Planner
  -> Action Executor
  -> Ledger
```

RSS / RSSHub 是第一批 trigger connector，不是完整 workflow engine。外部写动作默认 `dry-run`、`draft` 或 `approval_required`，直到 adapter、幂等和人工审批机制明确。

## 开发说明

扩展脚手架前，先阅读 `DEVELOP.md`、`AGENTS.md` 和 `docs/cli-tree.md`。新增命令时同步更新 CLI help、测试、README、MkDocs 页面和 changelog。
