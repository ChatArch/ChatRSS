# Development Guide

## CLI Rules

- Keep the real console script on `chatstyle>=0.2.0,<0.3.0` and use `add_tree_option()` for shared `--tree` / `--tree-brief` output from registered Click metadata.
- Keep the typed provider entry point on `chatenv>=0.2.10,<0.3.0`; use ChatEnv profile discovery and storage paths rather than package-local profile files.
- Prefer `CommandSchema`, `CommandField`, `add_interactive_option()`, and `resolve_command_inputs()` for new commands.
- Missing required args should auto-enter interactive mode when recoverable.
- `-i` forces interactive mode; `-I` disables prompting and must fail fast.
- Prompt defaults must match actual execution defaults.
- Sensitive values must stay masked in prompts and summaries.
- Prefer lazy imports in CLI wiring and keep implementation imports local when possible.

## Docs and Tests

- Use doc-first CLI testing.
- Put real CLI coverage under `tests/cli-tests/`.
- Put mock/fake CLI coverage under `tests/mock-cli-tests/`.
- Keep `README.md`, `docs/`, and `CHANGELOG.md` in sync with user-facing changes.
- Read back both `chatrss --tree` and `chatrss --tree-brief` after changing the command registry.

## Automation

- Keep automation small and reviewable.
- Prefer commands that can run in CI without interactive prompts.
- Ensure generated defaults are safe for local development.
