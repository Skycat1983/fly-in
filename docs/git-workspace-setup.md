# Git setup for a workspace with a read-only `.git` directory

## Instructions

### Use the repository in this workspace

Run these exports once in every new terminal session:

```sh
export GIT_DIR=/home/helaouta/Desktop/fly/.git-data
export GIT_WORK_TREE=/home/helaouta/Desktop/fly
```

Normal Git commands will then work:

```sh
git status
git add .
git commit -m "Describe the change"
git push
```

Do not add these exports globally to `~/.zshrc`. Global values would make Git use
this repository while you are working in other directories.

### Recreate this setup for an existing remote repository

From the project directory, create a writable metadata directory and connect it to
the remote:

```sh
git --git-dir=.git-data init --initial-branch=main
git --git-dir=.git-data config core.bare false
git --git-dir=.git-data remote add origin https://github.com/USER/REPOSITORY.git

export GIT_DIR="$PWD/.git-data"
export GIT_WORK_TREE="$PWD"

git fetch origin
git reset --mixed origin/main
git branch --set-upstream-to=origin/main main
git status
```

Make sure the project's `.gitignore` contains this entry before using `git add .`:

```gitignore
.git-data/
```

The mixed reset connects the local `main` branch to the fetched commit without
overwriting the files already present in the workspace. Review `git status` before
staging anything, especially when the workspace files might differ from the remote.

### Recreate this setup for a new, empty remote repository

From the project directory:

```sh
git --git-dir=.git-data init --initial-branch=main
git --git-dir=.git-data config core.bare false

export GIT_DIR="$PWD/.git-data"
export GIT_WORK_TREE="$PWD"

git config user.name "YOUR_GITHUB_USERNAME"
git config user.email "YOUR_EMAIL"
git remote add origin https://github.com/USER/REPOSITORY.git

git add .
git commit -m "Initial commit"
git push -u origin main
```

Add `.git-data/` to `.gitignore` before `git add .` so Git never tries to commit
its own internal database.

## How it works

A normal repository stores Git's internal data in a `.git` directory at the root
of its working tree. That data includes commits, branches, the staging index,
configuration, and remote URLs. The project files visible beside `.git` are the
working tree.

In this hosted workspace, `.git` is an empty, read-only mount controlled by the
platform. Running `git status` without extra configuration makes Git inspect that
directory. Because it does not contain repository metadata, Git reports that the
directory is not a repository. Git also cannot initialize it because the mount is
read-only.

Git does not require its metadata and working tree to be in the same directory.
The two environment variables tell it where each part lives:

- `GIT_DIR` points to the writable replacement for `.git`, which is `.git-data`.
- `GIT_WORK_TREE` points to the directory containing the actual project files.

Once those variables are exported, `git status`, `git add`, `git commit`, and
`git push` behave normally. Commits are created in `.git-data`, while changes are
read from the project directory. Pushing sends the commits from `.git-data` to the
configured GitHub remote.

The `.git-data` directory is persistent within this workspace and is ignored by
Git. It should not be copied into the repository or pushed to GitHub. The GitHub
repository remains the durable copy of the commit history if the hosted workspace
is later deleted or recreated.
