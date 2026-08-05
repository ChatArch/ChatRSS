from pathlib import Path


def test_chatarch_internal_dependencies_are_bounded_for_release():
    text = Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"chatstyle>=0.1.1,<0.2.0"' in text
    assert '"chatenv>=0.2.3,<0.3.0"' in text


def test_development_guide_documents_bounded_internal_dependencies():
    text = Path("DEVELOP.md").read_text(encoding="utf-8")

    assert "chatstyle>=0.1.1,<0.2.0" in text
    assert "chatenv>=0.2.3,<0.3.0" in text
    assert "chatstyle>=0.1.0" not in text
    assert "chatenv>=0.1.1" not in text
