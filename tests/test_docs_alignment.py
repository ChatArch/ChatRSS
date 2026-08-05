from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_cli_tree_documents_current_and_target_commands():
    text = _read("docs/cli-tree.md")

    assert "当前已实现命令树" in text
    assert "Minor 目标命令树" in text
    for command in ["init", "watch", "cat", "ps", "server", "flow"]:
        assert command in text
    for planned_group in ["trigger", "event", "router", "model", "action", "ledger", "connector"]:
        assert f"{planned_group} [规划]" in text
    assert "规划命令不能做成" in text


def test_mkdocs_nav_exposes_chatarch_docs_surfaces():
    text = _read("mkdocs.yml")

    assert "site_url: https://arch.gh.wzhecnu.cn/ChatRSS/" in text
    assert "mkdocs-static-i18n" not in text  # dependency lives in pyproject, config uses plugin name i18n
    for page in [
        "quickstart.md",
        "cli-tree.md",
        "capability-map.md",
        "interface-tree.md",
        "trigger-router-action.md",
        "practice-plan.md",
        "zulip-quickstart.md",
    ]:
        assert page in text


def test_chinese_default_zulip_page_has_english_mirror():
    zh = _read("docs/zulip-quickstart.md")
    en = _read("docs/zulip-quickstart.en.md")

    assert "# Zulip @mention 快速开始" in zh
    assert "# Zulip @mention Quick Start" in en
    assert "API key" in zh
    assert "API key" in en
