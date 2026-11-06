---
name: python-lint
description: Format and lint Python scripts with ruff. Use before committing Python changes or when configuring ruff.
---

# Python lint

Run `uvx ruff format`, then `uvx ruff check`, from the repo root. The rules come from `ruff.toml`;
don't pass rule flags or override them.
