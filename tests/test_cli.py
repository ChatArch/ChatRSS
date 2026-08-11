from click.testing import CliRunner
import json

from chatrss.cli import main


def test_main_help():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "--tree" in r.output
    assert "init" in r.output
    assert "watch" in r.output
    assert "cat" in r.output
    assert "flow" in r.output


def test_tree_option_renders_registered_command_surface():
    r = CliRunner().invoke(main, ["--tree"])

    assert r.exit_code == 0, r.output
    assert "chatrss" in r.output
    assert "├── --help" in r.output
    assert "├── --version" in r.output
    assert "├── --tree" in r.output
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


def test_version_option():
    r = CliRunner().invoke(main, ["--version"])
    assert r.exit_code == 0
    assert "chatrss, version 0.1.3" in r.output


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
