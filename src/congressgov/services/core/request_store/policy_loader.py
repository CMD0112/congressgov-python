"""Load request-store policy configuration from JSON or YAML files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .policy import ChangePolicy, PolicyConfig, PolicyRule

_DEFAULT_POLICY_FILE = Path(__file__).resolve().parent / "data" / "default_policies.json"


def _parse_policy(value: str) -> ChangePolicy:
    return ChangePolicy(str(value).lower())


def _rules_from_data(rules_data: list[dict[str, Any]]) -> tuple[PolicyRule, ...]:
    return tuple(
        PolicyRule(re.compile(item["pattern"]), _parse_policy(item["policy"]))
        for item in rules_data
    )


def policy_config_from_dict(data: dict[str, Any]) -> PolicyConfig:
    overrides = {
        str(path): _parse_policy(policy)
        for path, policy in (data.get("overrides") or {}).items()
    }
    rules_data = data.get("rules")
    rules = _rules_from_data(rules_data) if rules_data else None
    return PolicyConfig(
        default_policy=_parse_policy(data.get("default_policy", "moderate")),
        rules=rules if rules is not None else PolicyConfig().rules,
        overrides=overrides,
        closed_congress_permanent=bool(data.get("closed_congress_permanent", True)),
    )


def _load_raw(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "YAML policy files require PyYAML. Install with: pip install pyyaml"
            ) from exc
        loaded = yaml.safe_load(text)
    else:
        loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"Policy file must contain a mapping: {path}")
    return loaded


def load_policy_config(path: str | Path | None = None) -> PolicyConfig:
    """
    Load :class:`PolicyConfig` from *path* or the bundled default JSON file.

    Supports ``.json``, ``.yaml``, and ``.yml`` extensions.
    """
    policy_path = Path(path) if path is not None else _DEFAULT_POLICY_FILE
    return policy_config_from_dict(_load_raw(policy_path))
