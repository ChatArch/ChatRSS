# ChatRSS 快速开始

这页只覆盖当前已经可以运行的入口；规划中的 trigger/router/action 子命令见 [CLI 树](cli-tree.md)。

## 安装和检查

```bash
python -m pip install -e ".[dev,docs]"
chatrss --help
chatrss --tree
chatrss --tree-brief
chatrss --version
```

从源码目录临时运行：

```bash
PYTHONPATH=src python -m chatrss.cli --help
```

## 跑通本地 trigger-router-action 闭环

```bash
mkdir -p playground
chatrss flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

预期结果：

- `decision.decision` 是 `act`；
- actions 包含 `internal.notify`、`agent.run` 和 `github.comment`；
- ledger 中有 `event_received`、`route_decision`、`action_planned`、`action_result`。

如果没有全局命令：

```bash
PYTHONPATH=src python -m chatrss.cli flow demo --ledger ./playground/flow.ledger.jsonl --json-output
```

## 监听 GitHub / RSSHub feed

```bash
chatrss init ChatArch/ChatRSS --rsshub-url http://localhost:1200
chatrss watch ChatArch/ChatRSS --feeds issue,pull,comments --once --rsshub-url http://localhost:1200
```

`watch` 当前仍是 GitHub/RSSHub feed 监听器：它会读取 RSSHub route，做 seen 去重，然后把任务类事件发送给现有通知/文档动作。新的 Event Schema 和 Router seam 会逐步把这条路径迁移到统一 pipeline。

## 本地 RSSHub server 边界

```bash
chatrss server start --port 1200
chatrss server status
chatrss server logs --tail 50
chatrss server stop
```

`server` 命令基于 Docker / docker-compose。没有 Docker 的机器只能使用外部 RSSHub URL 或公共 feed，不能把 `server start` 当作必然可用的 smoke。

## 开发验证

```bash
python -m pytest -q
mkdocs build --strict
python -m build
```
