# GitHub repository setup

> **Maintainer documentation.** This page is for people maintaining the congressgov repository (releases, CI, codegen). If you're using the SDK, you don't need this — see the [user guide](../guide/USAGE.md) instead.

Use this checklist after creating a fresh **`CMD0112/congressgov-python`** repository on GitHub (empty, no template files required).

## 1. Push the project

Prefer a **new initial commit** on the empty GitHub repo (current tree only) so commit history does not carry old `Co-authored-by` trailers from other tooling. If you need to preserve history, rewrite messages locally before pushing.

```bash
git remote remove origin   # if an old remote exists
git remote add origin https://github.com/CMD0112/congressgov-python.git
git push -u origin main
```

Use your default branch name (`main` or `master`) consistently with [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

## 2. Enable Actions

**Settings → Actions → General** → allow GitHub Actions for this repository.

Workflows in this repo:

| Workflow | File | Trigger |
|----------|------|---------|
| CI | `.github/workflows/ci.yml` | Push / PR to `main` or `master` |
| Publish to PyPI | `.github/workflows/publish.yml` | GitHub Release published, or manual |

## 3. PyPI trusted publishing

Follow [PUBLISHING.md](PUBLISHING.md):

- PyPI project: **`congressgov`**
- Trusted publisher: owner **`CMD0112`**, repo **`congressgov-python`**, workflow **`publish.yml`**, environment **`pypi`**
- GitHub environment: **`pypi`** (name must match PyPI)

## 4. First release

1. Ensure `version` in `pyproject.toml` matches the tag (e.g. `2.0.0` → `v2.0.0`).
2. `git tag v2.0.0 && git push origin v2.0.0`
3. **Releases → New release** → publish the tag.

## Commits and attribution

All commits should list **human maintainers only**. Do not add `Co-authored-by` trailers for bots or IDE assistants. See [CONTRIBUTING.md](../../CONTRIBUTING.md).
