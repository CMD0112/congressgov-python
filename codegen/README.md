# Code generation package

Maintainer tooling to regenerate the client, models, and `congressgov.services` from OpenAPI.

**Documentation:** [docs/maintainers/CODEGEN.md](../docs/maintainers/CODEGEN.md)

```bash
poetry install --with codegen
poetry run python -m codegen validate-spec
poetry run python -m codegen generate-all
```
