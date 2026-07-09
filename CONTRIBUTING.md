# Contributing to congressgov-python

Source for the PyPI package [`congressgov`](https://pypi.org/project/congressgov/).

## Setup

```bash
git clone https://github.com/CMD0112/congressgov-python.git
cd congressgov-python
poetry install --with dev,cache,export,batch,codegen
cp .env.example .env   # add CONGRESS_API_KEY
```

### Wrong virtualenv (`No module named 'click'` / `codegen`)

If another project’s virtualenv is active, Poetry’s `poetry run` uses **that** interpreter, not this repo’s `.venv`, so optional `codegen` deps are missing.

```powershell
deactivate   # or: .\scripts\use-project-venv.ps1
poetry install --with dev,codegen
poetry run python -c "import click, codegen; print('ok')"
```

Use this repo’s own `.venv`, not another project’s, when working in this repository.

## Architecture

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for core vs optional extras and protected codegen paths.

## Quality checks

```bash
poetry run ruff check .
poetry run deptry .
poetry run mypy src/congressgov/services/client_factory.py
poetry build
```

Run `deptry` before adding dependencies to `pyproject.toml`; legacy reference modules under `codegen/data` are excluded via `[tool.deptry]`.

## Regenerating code

```bash
poetry run python -m codegen validate-spec
poetry run python -m codegen generate-all
```

See [docs/CODEGEN.md](docs/CODEGEN.md). CI runs `validate-spec` on every PR; `generate-all` drift must be clean before merge.

## Pull requests

- Document breaking API changes in [CHANGELOG.md](CHANGELOG.md)
- Update [README.md](README.md) and [docs/REFERENCE.md](docs/REFERENCE.md) when changing public APIs

## Commit messages

- Use only your own author name and email on commits.
- Do not add `Co-authored-by` or other trailers naming automated assistants or third-party tools.
