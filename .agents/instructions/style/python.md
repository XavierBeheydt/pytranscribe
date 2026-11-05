# Python style

Applies to every Python script in the repo.

- One standalone script per file, at the repo root, run with
  `uv run <script>.py`. Shared code is not factored into a module: each
  script stays self-contained.
- Scripts are named after their use case, not their engine:
  `pytranscribe-<use-case>.py` (`meeting`, `live`, `bot`…).
- Each script starts with the copyright header, then a PEP 723 metadata
  block. Dependencies are edited only through the
  [python-deps](../../skills/python-deps/SKILL.md) skill, never by hand:

  ```python
  # Copyright (c) <year> <name> <<email>>
  # /// script
  # requires-python = ">=3.13,<3.14"
  # dependencies = []
  # ///
  ```

- Python 3.13 (`.python-version`; whisperx does not support 3.14 yet); use
  native syntax: `list[str]`, `dict[str, int]`, `X | None`. No `from __future__ import annotations`, no
  `typing.List` / `Optional`.
- Type hints are mandatory on every function: all parameters and the return
  type.
- Entry point is `main() -> None`, called under `if __name__ == "__main__":`.
- Four spaces for indentation, lines up to 100 characters.
- `_name` is module-private. `__name` is for class internals ("protected",
  name-mangled).
- One line when the statement and its action are short:
  `if not items: return`, `for x in xs: seen.add(x)`.
- Simple conditional assignment is a ternary, not an `if`/`else` block:
  `label = "items" if items else "none"`.
- Ruff config lives in `ruff.toml`. Don't run `ruff format`: it expands
  one-line statements.
