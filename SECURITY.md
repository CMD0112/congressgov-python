# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 2.1.x   | Yes       |
| < 2.1   | No        |

## Reporting a vulnerability

If you discover a security issue, please report it privately rather than opening a public issue. Contact the maintainer via the email listed in `pyproject.toml` or GitHub security advisories for this repository.

## API keys

- **Never commit** Congress.gov API keys or `.env` files containing secrets.
- Use the `CONGRESS_API_KEY` environment variable or pass `token=` to `AuthenticatedClient` / `get_client_from_env()`.
- Copy [`.env.example`](.env.example) to `.env` for local development and keep `.env` out of version control.

## Dependencies

Keep dependencies updated via Poetry/pip and review release notes for `httpx`, `redis`, and other network-facing packages.
