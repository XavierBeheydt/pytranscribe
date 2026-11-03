---
name: todo-ai
description: Resolve the `TODO-AI` comments left in the repo, grouped logically, one plan and one subagent per group. Use when asked to handle, run or clear the TODO-AI.
---

# TODO-AI

Resolve the `TODO-AI: <description>` comments the user left in files, nearly
autonomously. Branches, worktrees, commits and PRs follow
`.agents/instructions/repo.md`.

1. **Collect.** `grep -rn "TODO-AI" --exclude-dir=.git --exclude-dir=.worktrees`.
   List each hit: file, line, description. None found: stop.
2. **Group.** A group is a set of similar TODOs that make one atomic change
   (e.g. one bugfix, one refactor, one feature); they touch the same area or
   depend on each other. Keep unrelated ones apart: there can be several
   groups, and each gets its own branch and PR. Show the groups to the user,
   and ask when a grouping is ambiguous.
3. **Plan.** For each group, write a short plan and a task list, each task
   with its check (see Coding Workflow in `AGENTS.md`).
4. **Dispatch.** One subagent per group, run in parallel, each in its own
   worktree and branch (`<type>/<short-description>`, from `dev`). Give each
   one: its TODOs, its plan and task list, and the instruction to follow
   `AGENTS.md` (style guide, lint, run, loop until green). A subagent
   touches only its group's files and never spawns others.
5. **Finish.** A subagent removes the `TODO-AI` comment in the change that
   resolves it, and reports: what changed, lint and run results, what is
   left. It does not commit or open a PR before the user has reviewed it.
6. **Report.** Summarise per group: branch, worktree, result, open points.
   A TODO that is unclear or fails its checks is left in place and reported,
   not guessed.
