# Repository workflow

Branches, worktrees, commits, pull requests, releases and tracking.
Read this before any git, branch, commit, PR or issue operation.

## Branches

- `main` — the default branch, protected: no deletion, no force push,
  changes only through a pull request, merged with a merge commit (no
  squash, no rebase). Never commit directly on `main`.
- `dev` — the permanent working branch, protected against deletion. Never
  delete it, locally or on the remote, even after a `dev` → `main` merge.
- Feature and fix branches — one per change, created from `dev`, named
  `<type>/<short-description>` where `<type>` is a Conventional Commits type:
  `feat/`, `fix/`, `docs/`, `refactor/`, `perf/`, `test/`, `build/`, `ci/`,
  `chore/`, `style/`, `revert/` (e.g. `feat/meeting-diarization`).
- Never enable automatic deletion of merged branches on the remote. Never
  delete a feature or fix branch without asking the user first.

## Worktrees

The repo root is the `dev` checkout. All other work happens in worktrees
under `.worktrees/`, ignored by git, one per branch and named after it, so
the path carries the Conventional Commits type. Create it from `dev`; once
the branch is merged and the user agrees, remove the worktree and its branch:

```sh
git worktree add -b feat/my-new-feature .worktrees/feat/my-new-feature dev
git worktree remove .worktrees/feat/my-new-feature
git branch -d feat/my-new-feature
```

## Commits

- Follow Conventional Commits:
  <https://www.conventionalcommits.org/en/v1.0.0/>. Read that spec when in
  doubt. Format: `type(scope): description`, with `!` after the type or
  scope, or a `BREAKING CHANGE:` footer, for a breaking change. The scope is
  the script or area touched (`meeting`, `agents`, `readme`…).
- Keep commits small and atomic: one coherent change, no unrelated work
  mixed in.
- Commit a step only after the user has reviewed it.
- An agent may co-sign its commits and PRs with its own name and the model
  used (`Co-Authored-By:` trailer, or the end of a PR description). If the
  user opposes it, don't.

## Pull requests

- Feature or fix branch → `dev`, merged with a squash merge. The PR title
  follows Conventional Commits: the squash keeps it as the commit message.
- `dev` → `main`, merged with a merge commit, never squashed: `dev` keeps
  its commits, and a squash would make the next merge conflict.
- Parked in-progress code (an experiment that doesn't work yet but is worth
  keeping) lives in a draft PR, with notes and findings in its description.

## Releases

Releases are tagged by hand as semver `vX.Y.Z`, right after the `dev` →
`main` PR (titled `chore(release): vX.Y.Z`) is merged. Tag the merge commit
of `main`, never `dev`. Never tag unless the user asks.

## Tracking

Work is tracked with the GitHub issues of the repo.
