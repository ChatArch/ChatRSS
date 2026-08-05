from pathlib import Path


def test_chatarch_internal_dependencies_are_bounded_for_release():
    text = Path("pyproject.toml").read_text(encoding="utf-8")

    assert '"chatstyle>=0.1.1,<0.2.0"' in text
    assert '"chatenv>=0.2.3,<0.3.0"' in text
