# Code generation package

Maintainer tooling to regenerate the client, models, and `congressgov.services` from OpenAPI.

**Documentation:** [docs/CODEGEN.md](../docs/CODEGEN.md)

```bash
poetry install --with codegen
poetry run python -m codegen validate-spec
poetry run python -m codegen generate-all
```
