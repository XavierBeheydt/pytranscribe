# AI Agents Instructions

The repo is a set of standalone Python scripts, one per file at the root, each
run with `uv run <script>.py`. No package, no `pyproject.toml`: every script
declares its own dependencies inline (PEP 723).

## The Eleven Commandments

For every agent, on every task:

1. Thou shalt state thy assumptions, and ask when unsure.
2. Thou shalt present every interpretation of a request, and never pick one
   silently.
3. Thou shalt propose the simpler solution when one exists, even against the
   user's idea.
4. Thou shalt stop and ask when something is unclear, saying exactly what.
5. Thou shalt do only what is asked: no hidden feature, no extra option or
   flexibility, except what a `TODO-AI` comment asks (see the
   [todo-ai](.agents/skills/todo-ai/SKILL.md) skill).
6. Thou shalt not handle errors that cannot happen.
7. Thou shalt be concise and compact, in writing and in code, without
   repetition, and rewrite in 50 lines what thou wrote in 200.
8. Thou shalt let the code explain itself, without an avalanche of comments.
9. Thou shalt follow the coding rules strictly. Where none exists, thou shalt
   neither invent one nor mix styles, but ask, and the rule gets added to
   `.agents/`.
10. Thou shalt not touch code next to the change, nor refactor working code,
    unless that is the request.
11. Thou shalt stay agnostic: nothing specific to a person or a machine
    (name, email, path, host) is hardcoded; read it from the configuration.

## Security

Never hardcode a login, password, token, key or any other secret, in code,
configs, docs, commits, PRs or issues. Read it from the environment or a
git-ignored file (e.g. `.env`), and commit only a placeholder file
(`.env.example`). Don't print or repeat a secret in a reply, and don't open
a secret file unless the task needs it. If a secret leaks, stop and tell the
user: it must be rotated, deleting the commit is not enough.

## Language

English is the language of the repo: code, comments, identifiers, docs,
commits and PRs. Interactive exchanges with the user use the user's language.

## Repository Workflow

Read [.agents/instructions/repo.md](.agents/instructions/repo.md) before any
git, branch, commit, PR or issue operation.

## Coding Workflow

A task is done only when one pass goes through with everything green:

1. Read the [style guide](.agents/instructions/style/python.md).
2. Code the feature or the fix, following the guide.
3. Format and lint with the [python-lint](.agents/skills/python-lint/SKILL.md) skill.
4. Run the script (`uv run <script>.py` with a sample input, or `--help`)
   and check its output.
5. If any step fails, fix and restart from step 2.

For a task of more than one step, state a short plan first, each step with
its check:

1. [Step] → verify: [check]
2. [Step] → verify: [check]

## Copyright header

Every new source or config file starts with a copyright header
(`Copyright (c) <year> <name> <<email>>`), in the file's comment syntax and
after the shebang if there is one. `<name>` and `<email>` come from
`git config user.name` and `git config user.email`; `<year>` is the current
year. If either is unset, ask instead of guessing.
Docs, generated files and files that can't hold comments have none.

## Skills

Procedures live in `.agents/skills/<name>/SKILL.md`; use the matching one
instead of improvising the command:

- [python-deps](.agents/skills/python-deps/SKILL.md): add, remove or update a
  script's dependencies (uv).
- [python-lint](.agents/skills/python-lint/SKILL.md): format and lint with ruff.
- [todo-ai](.agents/skills/todo-ai/SKILL.md): resolve the `TODO-AI` comments,
  grouped, one subagent per group.
