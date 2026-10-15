# Contributing

This guide covers how changes are made to this codebase. The main workflow revolves around opening an issue, working on a feature branch, and opening a pull request into `main`. The last section covers how maintainers version, tag, and release packages.

## Branches

| Branch | Purpose | Who writes to it |
| --- | --- | --- |
| `main` | Integration branch. Every change lands here through a pull request. | Pull requests only (maintainers push version bumps) |
| `stable` | Mirrors the latest `worm-shooter` release. This is the branch to run on the lab machine. | Maintainers only |
| `<pkg>/<type>/<issue>-<slug>` | Feature branches, one per issue. | The contributor working on the issue |

Both `main` and `stable` are protected. Do not push to them directly.

## Naming conventions

Branch names and commit messages share the same prefix structure:

```
<pkg>/<type>/<issue>-<slug>
```

- `<pkg>` is the **import name** of the package the change is for:

  | `<pkg>`   | Package        |
  | --------- | -------------- |
  | `shooter` | `worm-shooter` |
  | `axon`    | `axon-ui`      |
  | `axonkit` | `axon-ui-kit`  |

  If a change spans several packages, use the one that motivated it.

- `<type>` is one of:

  | `<type>`   | Use for                                        |
  | ---------- | ---------------------------------------------- |
  | `feat`     | New functionality                              |
  | `fix`      | Bug fixes                                      |
  | `refactor` | Code changes that do not change behavior       |
  | `style`    | Formatting-only code changes                   |
  | `test`     | Add or alter tests                             |
  | `docs`     | Documentation only                             |
  | `build`    | Dependencies, packaging, versions, tooling     |
  | `ops`      | Operational aspects like infrastructure, CI/CD |

- `<issue>` is the GitHub issue number.
- `<slug>` is a few lowercase words separated by hyphens.

Example for issue #30 about default marker coordinates:

| Thing | Format | Example |
| --- | --- | --- |
| Branch | `<pkg>/<type>/<issue>-<slug>` | `shooter/fix/30-default-coordinates` |
| Commit message | `<pkg>/<type>/<issue>-<slug>: <description>` | `shooter/fix/30-default-coordinates: update default marker coords` |

Write the part after the `:` in imperative mood ("update", "add", "remove", not "updated" or "adds") and keep the whole line under about 72 characters.

Pull request title follow a similar format but the slug can be dropped in favor of a description.

| Thing | Format | Example |
| --- | --- | --- |
| Pull request title | `<pkg>/<type>/<issue>: <description>` | `shooter/fix/30: correct default coordinates` |

Issue titles also follow a modified version of this format, instead dropping both the number and the slug.

| Thing | Format | Example |
| --- | --- | --- |
| Issue title | `<pkg>/<type>: <description>` | `shooter/fix: incorrect default coordinates` |

## Workflow

### 1. Open an issue

Every change starts with a GitHub issue, so there is a number to put in the branch name and a place to discuss the change before writing code.

- **Title:** in the format `<pkg>/<type>: <description>`, provide the main package the change would touch, the type of change (usually `fix` or `feat`) and a short description.
- **Body:**
  - For bugs: what happened, what you expected, and steps to reproduce. Mention which backends were used (real hardware or `mock`) and the app version shown on the start screen.
  - For features: what you want to do in the lab and why the current app makes it hard.

Wait for a maintainer to agree on the approach before starting larger changes.

### 2. Create a feature branch

Start from the latest `main`:

```bash
git switch main
git pull
git switch -c shooter/fix/30-default-coordinates
```

### 3. Commit to the branch

Make small, focused commits using the naming convention above:

```bash
git add -p
git commit -m "shooter/fix/30-default-coordinates: update default marker coords"
```

Try to break commits into small, auditable parts. When a commit is large, consider adding a description to the commit itself.

```bash
git commit # will open in editor
```

Push the branch to GitHub (the first push sets the upstream):

```bash
git push -u origin shooter/fix/30-default-coordinates
```

**Do not change package versions** (`version` in any `pyproject.toml`) in a feature branch. Versions are bumped by a maintainer at release time (see [Releases](#releases-maintainers)).

If `main` moves ahead while you are working, bring your branch up to date by merging `main` into it:

```bash
git fetch origin
git merge origin/main
```

### 4. Run the checks

Before opening a pull request, run these from the repository root and fix anything they report:

```bash
uv run ruff format
uv run ruff check
uv run ty check
uv run mypy -p shooter -p axon -p axonkit
```

There are no automated tests, so run the app and check your change by hand. Without lab hardware, use the mock backends:

```bash
uv run shooter --arduino-backend=mock --camera-backend=mock --data-backend=mock
```

If your change affects hardware behavior (stage movement, laser firing, serial packets, camera), say so in the pull request so it can be tested on the lab machine.

### 5. Open a pull request into `main`

Open a pull request from your branch into `main` on GitHub.

- **Title:** follow the naming convention above.
- **Body:**
  - What changed and why, in a few sentences.
  - How you tested it (mock backends, real hardware, or both).
  - `Closes #<issue>` on its own line, so the issue closes automatically when the pull request is merged.

Example body:

```markdown
Moves the default marker to the center of the feed plane instead of the
top-left corner.

Tested with mock backends; needs a check on the lab camera.

Closes #30
```

### 6. Review and merge

A maintainer reviews the pull request. Push more commits to the same branch to address feedback; the pull request updates automatically. Avoid force-pushing after review has started so reviewers can see what changed.

Once approved, a maintainer merges it with a **merge commit**, and the feature branch is deleted. If you still have the branch locally, clean it up with:

```bash
git switch main
git pull
git branch -d shooter/fix/30-default-coordinates
```

## Releases (maintainers)

Contributors do not need to do anything in this section. It documents how versions, tags, and the `stable` branch are managed.

### Versioning

Each package is versioned independently, using `MAJOR.MINOR.PATCH`:

| Bump | When (`worm-shooter`) | When (`axon-ui`, `axon-ui-kit` while `0.x`) |
| --- | --- | --- |
| `major` | Breaking change to the CSV data format, CLI, or lab workflow | Not used until `1.0.0` |
| `minor` | New features | Breaking API changes or new features |
| `patch` | Bug fixes only | Bug fixes only |

A package's version lives in its `packages/<name>/pyproject.toml` and is read at runtime through `importlib.metadata` (e.g. `shooter.VERSION`, shown on the start screen).

### Tags

Each release gets an annotated tag on the version bump commit:

| Package        | Tag                   | Tag message           |
| -------------- | --------------------- | --------------------- |
| `worm-shooter` | `worm-shooter-vX.Y.Z` | `Worm Shooter vX.Y.Z` |
| `axon-ui`      | `axon-ui-vX.Y.Z`      | `Axon UI vX.Y.Z`      |
| `axon-ui-kit`  | `axon-ui-kit-vX.Y.Z`  | `Axon UI Kit vX.Y.Z`  |

### Cutting a release

Releases are cut from `main` after the relevant pull requests are merged. Pushing the bump commit to the protected `main` branch requires a maintainer with permission to bypass branch protection.

1. Update `main`:

   ```bash
   git switch main
   git pull
   ```

2. Bump the version. `uv version` updates both the package's `pyproject.toml` and `uv.lock`. Use `--dry-run` first to check the result:

   ```bash
   uv version --package worm-shooter --bump patch --dry-run
   uv version --package worm-shooter --bump patch
   ```

   Replace `patch` with `minor` or `major` as needed.

3. Commit the bump on its own:

   ```bash
   git add packages/worm-shooter/pyproject.toml uv.lock
   git commit -m "shooter/build: bump version to 2.2.2"
   ```

4. Tag the commit:

   ```bash
   git tag -a worm-shooter-v2.2.2 -m "Worm Shooter v2.2.2"
   ```

5. Push the commit and the tag:

   ```bash
   git push origin main
   git push origin worm-shooter-v2.2.2
   ```

If a release includes changes to more than one package, bump, commit, and tag each package separately, libraries first (`axon-ui`, then `axon-ui-kit`, then `worm-shooter`).

### Updating `stable`

`stable` always points at the latest final `worm-shooter` release. After tagging a `worm-shooter` release, fast-forward `stable` to the tag:

```bash
git switch stable
git pull
git merge --ff-only worm-shooter-v2.2.2
git push origin stable
```

Library-only releases (`axon-ui`, `axon-ui-kit`) and release candidates do not move `stable`. Their changes reach `stable` with the next `worm-shooter` release.

If `git merge --ff-only` fails, `stable` has commits that are not on `main`. That should never happen; stop and find out why before forcing anything.
