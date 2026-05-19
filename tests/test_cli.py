from click.testing import CliRunner
from chatrss.cli import main


def test_main_help():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "init" in r.output
    assert "watch" in r.output
    assert "cat" in r.output


def test_init_help():
    r = CliRunner().invoke(main, ["init", "--help"])
    assert r.exit_code == 0


def test_watch_help():
    r = CliRunner().invoke(main, ["watch", "--help"])
    assert r.exit_code == 0
    assert "--rsshub-url" in r.output
    assert "--feeds" in r.output
