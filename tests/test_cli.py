from click.testing import CliRunner
import json

from chatrss.cli import main


def test_main_help():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "init" in r.output
    assert "watch" in r.output
    assert "cat" in r.output
    assert "flow" in r.output


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
