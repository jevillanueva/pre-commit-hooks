import os
import subprocess
import sys

DEFAULT_BASES = "main master develop dev staging stg"


def git(*args):
    res = subprocess.run(["git", *args], capture_output=True, text=True)
    return res.returncode, res.stdout.strip()


def main():
    to_ref = os.environ.get("PRE_COMMIT_TO_REF", "HEAD")
    bases = os.environ.get("NO_MERGE_BASE_BRANCHES", DEFAULT_BASES).split()

    remote_branch = os.environ.get("PRE_COMMIT_REMOTE_BRANCH", "")
    if remote_branch.startswith("refs/heads/"):
        branch = remote_branch[len("refs/heads/"):]
    else:
        _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch in bases:
        sys.stderr.write(f"Branch '{branch}' is a base branch, skipping merge check.\n")
        return 0

    exclude = []
    for b in bases:
        for ref in (f"refs/heads/{b}", f"refs/remotes/origin/{b}"):
            if git("rev-parse", "--verify", "-q", f"{ref}^{{commit}}")[0] == 0:
                exclude.append(ref)
    if not exclude:
        exclude = ["--remotes"]

    _, out = git("rev-list", "--merges", to_ref, "--not", *exclude)
    merges = out.split()
    if not merges:
        sys.stderr.write(f"No merge commits found on branch '{branch}'.\n")
        return 0

    sys.stderr.write(
        f"ERROR: merge commits found on '{branch}' (this repo uses rebase, not merge):\n"
    )
    for sha in merges:
        _, line = git("log", "--no-walk", "--format=  %h %s", sha)
        sys.stderr.write(line + "\n")
    sys.stderr.write("Fix: git rebase <base-branch>  (e.g. git rebase origin/main)\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
