<div align="center">
    <a href="https://pypi.python.org/pypi/chatrss">
        <img src="https://img.shields.io/pypi/v/chatrss.svg" alt="PyPI version" />
    </a>
    <a href="./.github/workflows/ci.yml">
        <img src="https://img.shields.io/badge/ci-github_actions-blue.svg" alt="Tests" />
    </a>
    <a href="./docs/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[English](README.en.md) | [简体中文](README.md)
</div>

# chatrss

chatrss package

## 快速开始

```bash
pip install -e ".[dev]"
chatrss hello ChatArch
python -m pytest -q
python -m build
```

## 处理策略

`chatrss watch` 现在按任务导向处理新事件：

- `issue` / `pull` / `comments`：视为待处理任务，发送飞书通知并追加文档事件行。
- `repo_event`：视为背景上下文，只落本地 JSONL，避免噪音。
- 通知文案强调“先完成当前任务，再看是否需要整理/封装”。


## Trigger-Router-Action MVP

`chatrss flow demo` 可以在本地跑通最小 trigger-router-action 闭环：内置示例事件会被标准化为 Event，经规则和 model-router stub 判断后，生成 dry-run action 并写入 JSONL ledger。

```bash
chatrss flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

这个 MVP 用来验证新的 minor 版本方向：RSS/RSSHub 先作为 trigger connector，后续再连接真实社区对话源、GitHub 项目进展、模型判断和 action adapter。

## CLI 规范

这个模板默认依赖 `chatstyle>=0.1.0` 和 `chatenv>=0.1.1`，新的命令应优先使用：

- `CommandSchema` / `CommandField` 描述输入。
- `add_interactive_option()` 提供统一 `-i/-I`。
- `resolve_command_inputs()` 统一缺参补问、默认值、TTY 与校验。

## 目录结构

- `src/`：包源码
- `tests/code-tests/`：代码测试和历史测试迁移
- `tests/cli-tests/`：真实 CLI 测试，doc-first
- `tests/mock-cli-tests/`：mock/fake CLI 测试，doc-first
- `docs/`：长期维护文档，由 mkdocs 构建

## 开发说明

扩展脚手架前，先阅读 `DEVELOP.md` 和 `AGENTS.md`。
