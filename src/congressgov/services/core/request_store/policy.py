"""Change-likelihood policies controlling when stored responses may be refetched."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from .models import StoredResponse


class ChangePolicy(str, Enum):
    """How quickly a stored response is considered stale."""

    PERMANENT = "permanent"
    STATIC = "static"
    STABLE = "stable"
    MODERATE = "moderate"
    DYNAMIC = "dynamic"
    VOLATILE = "volatile"


# Seconds until a stored entry is eligible for automatic refresh (None = never).
POLICY_TTLS: dict[ChangePolicy, int | None] = {
    ChangePolicy.PERMANENT: None,
    ChangePolicy.STATIC: 7 * 86400,
    ChangePolicy.STABLE: 86400,
    ChangePolicy.MODERATE: 3600,
    ChangePolicy.DYNAMIC: 300,
    ChangePolicy.VOLATILE: 60,
}


@dataclass(frozen=True, slots=True)
class StalenessEstimate:
    """Estimated freshness of a stored response based on fetch time and policy."""

    policy: ChangePolicy
    fetched_at: datetime
    ttl_seconds: int | None
    age_seconds: float
    remaining_seconds: float | None
    is_stale: bool
    refresh_after: datetime | None
    change_likelihood: float

    @property
    def likely_changed(self) -> bool:
        """True when change likelihood exceeds 50%."""
        return self.change_likelihood >= 0.5


@dataclass
class PolicyRule:
    """Map URL path patterns to a :class:`ChangePolicy`."""

    pattern: re.Pattern[str]
    policy: ChangePolicy


DEFAULT_POLICY_RULES: tuple[PolicyRule, ...] = (
    PolicyRule(re.compile(r"^/bill/?$"), ChangePolicy.DYNAMIC),
    PolicyRule(re.compile(r"^/member/?$"), ChangePolicy.DYNAMIC),
    PolicyRule(re.compile(r"^/amendment/?$"), ChangePolicy.DYNAMIC),
    PolicyRule(re.compile(r"^/committee/?$"), ChangePolicy.STABLE),
    PolicyRule(re.compile(r"^/congress/?$"), ChangePolicy.STATIC),
    PolicyRule(re.compile(r"^/law/?$"), ChangePolicy.STATIC),
    PolicyRule(re.compile(r"^/member/[^/]+/(?:sponsored|cosponsored)-legislation"), ChangePolicy.DYNAMIC),
    PolicyRule(re.compile(r"^/member/[^/]+$"), ChangePolicy.STABLE),
    PolicyRule(re.compile(r"^/bill/[^/]+/[^/]+/[^/]+/"), ChangePolicy.MODERATE),
    PolicyRule(re.compile(r"^/bill/[^/]+/[^/]+/[^/]+$"), ChangePolicy.MODERATE),
    PolicyRule(re.compile(r"^/amendment/"), ChangePolicy.MODERATE),
    PolicyRule(re.compile(r"^/committee/"), ChangePolicy.STABLE),
    PolicyRule(re.compile(r"^/nomination/"), ChangePolicy.MODERATE),
    PolicyRule(re.compile(r"^/house-vote/"), ChangePolicy.STATIC),
    PolicyRule(re.compile(r"^/senate-vote/"), ChangePolicy.STATIC),
)


_CONGRESS_IN_PATH = re.compile(
    r"^/(?:bill|amendment|law|nomination|house-vote|senate-vote)/(\d+)"
)


def current_congress(*, year: int | None = None) -> int:
    """Estimate the current Congress number from the calendar year."""
    moment = year if year is not None else datetime.now(timezone.utc).year
    return (moment - 1789) // 2 + 1


def extract_congress_from_path(path: str) -> int | None:
    match = _CONGRESS_IN_PATH.match(path)
    if match is None:
        return None
    return int(match.group(1))


@dataclass
class PolicyConfig:
    """Resolved policy configuration for the request store."""

    default_policy: ChangePolicy = ChangePolicy.MODERATE
    rules: tuple[PolicyRule, ...] = field(default_factory=lambda: DEFAULT_POLICY_RULES)
    overrides: dict[str, ChangePolicy] = field(default_factory=dict)
    closed_congress_permanent: bool = True

    def resolve(self, path: str) -> ChangePolicy:
        if self.closed_congress_permanent:
            congress = extract_congress_from_path(path)
            if congress is not None and congress < current_congress() - 1:
                return ChangePolicy.PERMANENT
        if path in self.overrides:
            return self.overrides[path]
        for rule in self.rules:
            # match(), not search(): rule patterns describe path *prefixes*.
            # search() would let an unanchored custom rule (e.g. one without a
            # leading "^", as loaded from policy_loader.py) match anywhere
            # mid-path instead of only at the start.
            if rule.pattern.match(path):
                return rule.policy
        return self.default_policy


def estimate_staleness(
    stored: StoredResponse,
    *,
    policy: ChangePolicy | None = None,
    now: datetime | None = None,
) -> StalenessEstimate:
    """
    Estimate how likely a stored response has changed since it was fetched.

    ``change_likelihood`` ramps from 0.0 at fetch time to 1.0 at TTL expiry
    (sigmoid curve). ``PERMANENT`` entries always report 0.0 unless already
    forced stale by external logic.
    """
    resolved = policy or ChangePolicy(stored.policy)
    ttl = POLICY_TTLS.get(resolved)
    moment = now or datetime.now(timezone.utc)
    # TTL/age is always anchored to when *we* fetched the response, not the API's
    # own `updateDate` (`source_updated_at`), which is frequently a stale historical
    # timestamp on the source record and would otherwise make freshly stored
    # responses look immediately expired. `source_updated_at` remains available on
    # `StoredResponse` for change-detection use cases, just not for TTL math.
    fetched = stored.fetched_at
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    age_seconds = max(0.0, (moment - fetched).total_seconds())

    if ttl is None:
        return StalenessEstimate(
            policy=resolved,
            fetched_at=fetched,
            ttl_seconds=None,
            age_seconds=age_seconds,
            remaining_seconds=None,
            is_stale=False,
            refresh_after=None,
            change_likelihood=0.0,
        )

    remaining = max(0.0, ttl - age_seconds)
    stale = age_seconds > ttl
    progress = min(1.0, age_seconds / ttl) if ttl else 0.0
    # Smooth likelihood curve — low early, rises sharply near TTL.
    likelihood = progress ** 2

    refresh_after = None
    if not stale:
        refresh_after = datetime.fromtimestamp(fetched.timestamp() + ttl, tz=timezone.utc)

    return StalenessEstimate(
        policy=resolved,
        fetched_at=fetched,
        ttl_seconds=ttl,
        age_seconds=age_seconds,
        remaining_seconds=remaining if not stale else 0.0,
        is_stale=stale,
        refresh_after=refresh_after,
        change_likelihood=likelihood if not stale else 1.0,
    )


def is_stale(
    stored: StoredResponse,
    *,
    now: datetime | None = None,
    policy: ChangePolicy | None = None,
) -> bool:
    """
    Return True when a stored response should be refreshed automatically.

    ``PERMANENT`` entries never go stale unless ``force_fetch`` is used.
    """
    return estimate_staleness(stored, policy=policy, now=now).is_stale


def estimate_refresh_after(
    stored: StoredResponse,
    *,
    policy: ChangePolicy | None = None,
) -> datetime | None:
    """
    Estimate when a stored entry becomes eligible for automatic refresh.

    Returns ``None`` for permanent entries or when already stale.
    """
    return estimate_staleness(stored, policy=policy).refresh_after
