#!/usr/bin/env bash
# Fails if commits between the branch fork point and HEAD include merge commits.
# Env: NO_MERGE_BASE_BRANCHES (space separated, default "main master develop")
set -u

to_ref="${PRE_COMMIT_TO_REF:-HEAD}"
branch="$(git rev-parse --abbrev-ref "$to_ref" 2>/dev/null || echo "$to_ref")"

# Only validate feature/fix style branches, not the base branches themselves.
bases="${NO_MERGE_BASE_BRANCHES:-main master dev develop stg staging}"
for b in $bases; do
  [ "$branch" = "$b" ] && exit 0
done

# Exclude everything reachable from base branches so only the branch's own commits are checked.
exclude=()
for b in $bases; do
  for r in "refs/heads/$b" "refs/remotes/origin/$b"; do
    git rev-parse --verify -q "$r^{commit}" >/dev/null && exclude+=("$r")
  done
done
if [ ${#exclude[@]} -eq 0 ]; then
  exclude=(--remotes)
fi

merges="$(git rev-list --merges --min-parents=2 "$to_ref" --not "${exclude[@]}")"
[ -z "$merges" ] && exit 0

echo "ERROR: merge commits found on '$branch' (this repo uses rebase, not merge):" >&2
git log --no-walk --format='  %h %s' $merges >&2
echo "Fix: git rebase <base-branch>  (e.g. git rebase origin/main)" >&2
exit 1
