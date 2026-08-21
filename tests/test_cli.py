import json
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner
from chatstyle import render_click_tree

from chatrss import __version__
import chatrss.cli as cli
from chatrss.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_main_help():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "--tree" in r.output
    assert "--tree-brief" in r.output
    assert "init" in r.output
    assert "watch" in r.output
    assert "cat" in r.output
    assert "flow" in r.output


def test_tree_option_renders_registered_command_surface():
    r = CliRunner().invoke(main, ["--tree"])

    assert r.exit_code == 0, r.output
    assert r.output.strip() == render_click_tree(main, root_name="chatrss")
    assert r.output.splitlines()[0] == "chatrss"
    assert r.output.splitlines().count("chatrss") == 1
    assert "├── --help" in r.output
    assert "├── --version" in r.output
    assert "├── --tree" in r.output
    assert "├── --tree-brief" in r.output
    assert "server" in r.output
    assert "start [--port PORT]" in r.output
    assert "logs [--tail TAIL]" in r.output
    assert "init [REPO]" in r.output
    assert "watch [REPO]" in r.output
    assert "cat [REPO]" in r.output
    assert "flow" in r.output
    assert "demo [--ledger LEDGER] [--json-output]" in r.output
    assert "ps" in r.output
    assert "hello" not in r.output.lower()


def test_tree_brief_renders_same_surface_without_signatures():
    r = CliRunner().invoke(main, ["--tree-brief"])

    assert r.exit_code == 0, r.output
    assert r.output.strip() == render_click_tree(main, root_name="chatrss", brief=True)
    assert "server  # 管理本地 RSSHub Docker 服务；可能变更容器状态。" in r.output
    assert "demo  # 用内置事件 dry-run action 并写 JSONL ledger。" in r.output
    assert "[REPO]" not in r.output
    assert "[--port PORT]" not in r.output
    assert "[--json-output]" not in r.output


def test_tree_root_uses_public_console_command_in_module_mode():
    r = CliRunner().invoke(main, ["--tree"], prog_name="python -m chatrss.cli")

    assert r.exit_code == 0, r.output
    assert r.output.splitlines()[0] == "chatrss"
    assert "python -m chatrss.cli" not in r.output


def test_version_option():
    r = CliRunner().invoke(main, ["--version"])
    assert r.exit_code == 0
    assert f"chatrss, version {__version__}" in r.output


def test_init_help():
    r = CliRunner().invoke(main, ["init", "--help"])
    assert r.exit_code == 0


def test_watch_help():
    r = CliRunner().invoke(main, ["watch", "--help"])
    assert r.exit_code == 0
    assert "--rsshub-url" in r.output
    assert "--feeds" in r.output


def test_flow_demo_json_output(tmp_path):
    ledger = tmp_path / "flow.ledger.jsonl"

    r = CliRunner().invoke(main, ["flow", "demo", "--ledger", str(ledger), "--json-output"])

    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["decision"]["decision"] == "act"
    assert {action["type"] for action in data["actions"]} == {
        "internal.notify",
        "agent.run",
        "github.comment",
    }
    assert ledger.exists()


def test_watch_does_not_echo_document_token_or_user_id(monkeypatch):
    fake_config = SimpleNamespace(
        CHATRSS_DEFAULT_REPO=SimpleNamespace(value=None),
        CHATRSS_RSSHUB_URL=SimpleNamespace(value=None),
        CHATRSS_LARK_DOC_TOKEN=SimpleNamespace(value=None),
        CHATRSS_LARK_USER_ID=SimpleNamespace(value=None),
    )
    monkeypatch.setattr(cli, "_load_config", lambda: fake_config)
    monkeypatch.setattr("chatrss.watcher.poll_once", lambda *_args, **_kwargs: [])

    result = CliRunner().invoke(
        main,
        [
            "watch",
            "ChatArch/ChatRSS",
            "--rsshub-url",
            "https://rsshub.example.invalid",
            "--doc",
            "secret-document-token",
            "--notify-user",
            "secret-user-id",
            "--once",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "secret-document-token" not in result.output
    assert "secret-user-id" not in result.output
    assert result.output.count("已配置（值不回显）") == 2


def test_documented_tree_matches_registered_surface():
    tree = render_click_tree(main, root_name="chatrss")
    brief_tree = render_click_tree(main, root_name="chatrss", brief=True)

    for relative_path in ("docs/cli-tree.md", "docs/cli-tree.en.md"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert f"```text\n{tree}\n```" in text
        assert f"```text\n{brief_tree}\n```" in text
