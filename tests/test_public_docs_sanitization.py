from pathlib import Path
import re


PUBLIC_MARKDOWN = [
    Path("README.md"),
    Path("README.en.md"),
    Path("CHANGELOG.md"),
    *Path("docs").rglob("*.md"),
]


FORBIDDEN_PATTERNS = {
    "unix_home_path": re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+"),
    "playground_project_path": re.compile(r"Playground/projects/"),
    "chatarch_secret_store_path": re.compile(r"\.chatarch/"),
    "secret_path_segment": re.compile(r"(?:^|[\s`'\"])(?:secrets|secret)/"),
    "env_artifact_name": re.compile(r"\b[A-Za-z0-9_.-]+\.env\b"),
    "secret_bearing_env_key": re.compile(
        r"\b[A-Z][A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET|API_KEY)[A-Z0-9_]*\b"
    ),
    "internal_ddns_host": re.compile(r"\b[A-Za-z0-9-]+\.oray\b"),
    "local_email_domain": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.local\b"),
    "chatarch_local_domain": re.compile(r"\b(?:[A-Za-z0-9-]+\.)?chatarch\.local\b"),
    "local_domain_alias": re.compile(
        r"\b[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.local(?:\.[A-Za-z0-9-]+)*\b"
    ),
}


def test_public_markdown_uses_placeholders_for_private_hosts_paths_and_secret_keys():
    offenders = []
    for path in PUBLIC_MARKDOWN:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                offenders.append(f"{path}:{name}")

    assert offenders == []
