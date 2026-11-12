# pre-commit-hooks

Custom [pre-commit](https://pre-commit.com) hooks. Works on Linux, macOS and Windows (pure Python).

## Hooks

### `no-merge-commits` (pre-push)

For rebase-based workflows. Blocks a push when the branch contains merge commits, from the point it was created (`git checkout -b`) up to the last commit.

How it works:

- Checks only commits on the branch that are **not** reachable from the base branches (`main`, `master`, `develop`, local or `origin/`).
- Any merge commit in that set (for example from `git merge main` into your feature branch) fails the hook.
- Pushes of the base branches themselves are skipped.
- If no base branch exists, it falls back to excluding all remote branches.

Configuration (environment variable):

| Variable | Default | Description |
|---|---|---|
| `NO_MERGE_BASE_BRANCHES` | `main master develop` | Space-separated base branches |

## Usage

Add to your project's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/jevillanueva/pre-commit-hooks
    rev: v0.2.0
    hooks:
      - id: no-merge-commits
```

Install the pre-push hook:

```bash
pip install pre-commit
pre-commit install --hook-type pre-push
```

Run manually:

```bash
pre-commit run no-merge-commits --hook-stage pre-push --all-files
```

Fix a failing push by rebasing instead of merging:

```bash
git fetch origin
git rebase origin/main
git push --force-with-lease
```

## Local development

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install pre-commit .
```

Test without changing a project's config:

```bash
cd /path/to/project
pre-commit try-repo /path/to/pre-commit-hooks no-merge-commits --hook-stage pre-push --verbose
```

`pre-commit` requires this repo to be a git repo with a commit; tag releases (`git tag v0.2.0`) and use the tag as `rev`.
