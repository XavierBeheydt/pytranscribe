---
name: python-deps
description: Add, remove or update a script's inline (PEP 723) dependencies with uv. Use when a script needs a new package or a dependency change.
---

# Python dependencies

Each script carries its own dependencies in its `# /// script` block; edit
them with uv, never by hand:

- `uv add --script <script>.py <package>` adds a dependency.
- `uv remove --script <script>.py <package>` removes one.
- `uv run <script>.py` installs what the block lists and runs the script.
