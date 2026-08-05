from pathlib import Path

import yaml


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
        "real-world-cases.md",
        "zulip-quickstart.md",
    ]:
        assert page in text


def test_preview_workflow_parses_and_uses_chatarch_url():
    text = _read(".github/workflows/preview.yaml")
    data = yaml.safe_load(text)

    assert data["name"] == "Preview Docs"
    assert "jobs" in data
    assert "github.io" not in text
    assert "CHATARCH_PREVIEW_URL" in text
    assert "\\nPreview available at:" in text


def test_chinese_default_zulip_page_has_english_mirror():
    zh = _read("docs/zulip-quickstart.md")
    en = _read("docs/zulip-quickstart.en.md")

    assert "# Zulip @mention 快速开始" in zh
    assert "# Zulip @mention Quick Start" in en
    assert "API key" in zh
    assert "API key" in en


def test_real_world_case_documents_complete_zulip_reply_loop():
    zh = _read("docs/real-world-cases.md")
    en = _read("docs/real-world-cases.en.md")
    nav = _read("mkdocs.yml")

    for text in [zh, en]:
        assert "codex-plan-20260805012352" in text
        assert "zulip:message:20:mention:chatrss-watcher@chatarch.local" in text
        assert "zulip.message.reply" in text
        assert "action_verified" in text
        assert "message_id=21" in text
        assert "API key" in text
    assert "real-world-cases.md" in nav
    assert "Real-World Event Cases" in nav


def test_zulip_quickstart_links_to_complete_case():
    zh = _read("docs/zulip-quickstart.md")
    en = _read("docs/zulip-quickstart.en.md")

    assert "真实事件案例" in zh
    assert "real-world cases" in en
    assert "near/21" in zh
    assert "near/21" in en
