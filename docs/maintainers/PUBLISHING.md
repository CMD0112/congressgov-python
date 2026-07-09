# Publishing to PyPI

> **Maintainer documentation.** This page is for people maintaining the congressgov repository (releases, CI, codegen). If you're using the SDK, you don't need this — see the [user guide](../guide/USAGE.md) instead.

Publish via **GitHub Actions trusted publishing** (no long-lived PyPI API token in the repo).

If you just recreated the GitHub repository, start with [GITHUB_SETUP.md](GITHUB_SETUP.md).

After the first release, install with:

```bash
poetry add "congressgov>=2.0.0"
# or: pip install "congressgov>=2.0.0"
```

**1.0.0** did not include the `congressgov` import package. Yank **1.0.0** on PyPI after **1.1.0** is live so new installs cannot resolve the broken release:

```bash
twine yank --version 1.0.0 --reason "Missing congressgov module; use >=1.1.0" congressgov
```

## Pre-release checklist

Complete these before tagging **v2.1.0** (or any release):

- [ ] All CI checks green on `main` (`pytest`, `ruff`, `deptry`, `audit-client-compat`, `api-coverage-matrix --check --check-service-methods`)
- [ ] `pyproject.toml` version matches the git tag (e.g. `2.1.0` → `v2.1.0`)
- [ ] Version bump is committed and pushed to `main` **before** creating the tag
- [ ] [`CHANGELOG.md`](../../CHANGELOG.md) documents the release
- [ ] Local wheel smoke: `poetry build` and `pip install dist/congressgov-*.whl`
- [ ] PyPI project `congressgov` exists (or you own the name you publish under)
- [ ] PyPI **trusted publisher** configured (see below)
- [ ] GitHub **environment** `pypi` exists (see below)
- [ ] Git tag pushed: `git tag v2.1.0 && git push origin v2.1.0`
- [ ] **GitHub Release** created for that tag (triggers publish workflow)

## Trusted publishing setup (one-time)

### 1. PyPI project

1. Sign in at [pypi.org](https://pypi.org).
2. Create project **`congressgov`** (must match `[project] name` in `pyproject.toml`), or claim an existing project you maintain.

### 2. PyPI trusted publisher

On the PyPI project: **Publishing** → **Add a new pending publisher** (GitHub):

| Field | Value |
|-------|--------|
| Owner | `CMD0112` |
| Repository name | `congressgov-python` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Save the pending publisher. It becomes active after the first successful publish from that workflow.

### 3. GitHub environment

In **GitHub → CMD0112/congressgov-python → Settings → Environments**:

1. **New environment** → name: `pypi`
2. (Optional) Add protection rules: required reviewers, wait timer, or restrict to `main` branch
3. Save

The publish workflow [`.github/workflows/publish.yml`](../../.github/workflows/publish.yml) uses `environment: pypi`, which must match the PyPI trusted publisher environment name.

### 4. Publish a release

**Recommended (release tag):**

```bash
# After pyproject.toml + CHANGELOG for 2.1.0 are on main:
git tag v2.1.0
git push origin v2.1.0
```

Then on GitHub: **Releases → Draft a new release** → choose tag `v2.1.0` → **Publish release**.

The publish workflow checks out `refs/tags/vX.Y.Z` (not the release target commit alone), verifies `HEAD` matches the tag, and fails if `poetry version -s` ≠ tag.

That runs the workflow and uploads to PyPI via OIDC.

**Manual trigger (maintainers):** **Actions → Publish to PyPI → Run workflow**. Optionally set **tag** to `v2.1.0` to checkout that tag and run the same version checks as a release. Prefer GitHub Releases for production.

The workflow runs `poetry build`, a wheel import smoke test (`import congressgov`), verifies `codegen` is not in the wheel, and `pypa/gh-action-pypi-publish` with `id-token: write` for trusted publishing. **`skip-existing: true`** lets you re-run the workflow when that version is already on PyPI (otherwise PyPI returns `400 File already exists`).

To ship **new** code after a version is on PyPI, bump `version` in `pyproject.toml`, tag `vX.Y.Z`, and publish a new GitHub release — you cannot replace files for an existing version.

## Local smoke install

```bash
poetry build
pip install dist/congressgov-2.0.4-*.whl
python -c "from congressgov import Bill, get_client_from_env; print('ok')"
```

## Versioning

- **1.1.x**: `congressgov` import facade; see [VERSIONING.md](../guide/VERSIONING.md) and [MIGRATION.md](../guide/MIGRATION.md)
- Tag format must be `vX.Y.Z` and match `version` in `pyproject.toml` for release-triggered publishes
