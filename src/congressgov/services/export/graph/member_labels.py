"""Congressional member display labels for network graph nodes."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Protocol

from .models import GraphMemberNode

if TYPE_CHECKING:
    from congressgov.models.entities.member import Member, Term

CANONICAL_LABEL_RE = re.compile(
    r"^(?P<title>Rep\.|Sen\.)\s+(?P<name>.+?)\s+"
    r"\[(?P<party>[A-Z?])-(?P<state>[A-Z?]{2})(?:-(?P<district>\d+))?\]$"
)
TITLE_PREFIX_RE = re.compile(r"^(Rep\.|Sen\.)\s+", re.IGNORECASE)

PARTY_ALIASES: dict[str, str] = {
    "d": "D",
    "dem": "D",
    "democrat": "D",
    "democratic": "D",
    "r": "R",
    "rep": "R",
    "republican": "R",
    "i": "I",
    "ind": "I",
    "independent": "I",
}


def normalize_party_code(party: str | None) -> str | None:
    """Normalize party names to a single-letter code when possible."""
    if party is None:
        return None
    text = str(party).strip()
    if not text:
        return None
    if len(text) == 1 and text.upper() in {"D", "R", "I"}:
        return text.upper()
    mapped = PARTY_ALIASES.get(text.lower())
    if mapped:
        return mapped
    upper = text.upper()
    if upper in {"D", "R", "I"}:
        return upper
    return upper[:1]


def _normalize_state_code(state: str | None) -> str | None:
    if state is None:
        return None
    text = str(state).strip().upper()
    return text[:2] if text else None


def _normalize_district(district: int | str | None) -> str | None:
    if district is None:
        return None
    text = str(district).strip()
    if not text:
        return None
    if text.isdigit():
        return str(int(text))
    return text


def _title_prefix(
    *,
    district: int | str | None,
    chamber: str | None,
    origin_chamber: str | None,
    existing_title: str | None,
) -> str:
    if existing_title in {"Rep.", "Sen."}:
        return existing_title
    chamber_value = (chamber or origin_chamber or "").strip().lower()
    if chamber_value == "senate":
        return "Sen."
    if chamber_value == "house":
        return "Rep."
    if _normalize_district(district) is not None:
        return "Rep."
    if existing_title:
        return existing_title
    return "Rep."


def _parse_name_parts(
    *,
    full_name: str | None,
    first_name: str | None,
    middle_name: str | None,
    last_name: str | None,
    bioguide_id: str,
) -> tuple[str | None, str | None, str | None]:
    """Return (title_prefix, composed_name, existing_bracket) from raw fields."""
    existing_title: str | None = None
    name_body = full_name.strip() if full_name else ""

    if name_body:
        canonical = CANONICAL_LABEL_RE.match(name_body)
        if canonical:
            return (
                canonical.group("title"),
                canonical.group("name").strip(),
                (
                    f"[{canonical.group('party')}-{canonical.group('state')}"
                    f"{('-' + canonical.group('district')) if canonical.group('district') else ''}]"
                ),
            )
        title_match = TITLE_PREFIX_RE.match(name_body)
        if title_match:
            existing_title = title_match.group(1)
            if existing_title.lower().startswith("sen"):
                existing_title = "Sen."
            else:
                existing_title = "Rep."
            name_body = name_body[title_match.end() :].strip()

        bracket_index = name_body.rfind("[")
        existing_bracket = None
        if bracket_index > 0 and name_body.endswith("]"):
            existing_bracket = name_body[bracket_index:].strip()
            name_body = name_body[:bracket_index].strip().rstrip(",").strip()

        if "," in name_body:
            return existing_title, name_body, existing_bracket

        tokens = name_body.split()
        if len(tokens) >= 2:
            last = tokens[-1]
            first = " ".join(tokens[:-1])
            composed = f"{last}, {first}"
            return existing_title, composed, existing_bracket
        if tokens:
            return existing_title, tokens[0], existing_bracket

    if last_name:
        first_parts = [part for part in (first_name, middle_name) if part]
        first = " ".join(first_parts) if first_parts else None
        if first:
            return existing_title, f"{last_name}, {first}", None
        return existing_title, last_name, None

    if first_name:
        return existing_title, first_name, None

    return existing_title, bioguide_id, None


def _compose_bracket(
    *,
    party: str | None,
    state: str | None,
    district: int | str | None,
    title: str,
    existing_bracket: str | None,
) -> str:
    if existing_bracket:
        bracket_match = re.match(
            r"^\[(?P<party>[A-Z?])-(?P<state>[A-Z?]{2})(?:-(?P<district>\d+))?\]$",
            existing_bracket,
        )
        if bracket_match and party is None and state is None and district is None:
            return existing_bracket

    party_code = normalize_party_code(party) or "?"
    state_code = _normalize_state_code(state) or "?"
    district_code = _normalize_district(district)
    if title == "Rep." and district_code is not None:
        return f"[{party_code}-{state_code}-{district_code}]"
    return f"[{party_code}-{state_code}]"


def format_congress_member_label(
    *,
    bioguide_id: str,
    full_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    last_name: str | None = None,
    party: str | None = None,
    state: str | None = None,
    district: int | str | None = None,
    chamber: str | None = None,
    origin_chamber: str | None = None,
) -> str:
    """Format ``Rep./Sen. Last, First [Party-State-District]`` for graph nodes."""
    parsed_title, composed_name, existing_bracket = _parse_name_parts(
        full_name=full_name,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        bioguide_id=bioguide_id,
    )

    if full_name:
        canonical = CANONICAL_LABEL_RE.match(full_name.strip())
        if canonical:
            party_code = normalize_party_code(party) or canonical.group("party")
            state_code = _normalize_state_code(state) or canonical.group("state")
            district_code = _normalize_district(district) or canonical.group("district")
            title = canonical.group("title")
            name = canonical.group("name").strip()
            if title == "Rep." and district_code is not None:
                bracket = f"[{party_code}-{state_code}-{district_code}]"
            else:
                bracket = f"[{party_code}-{state_code}]"
            return f"{title} {name} {bracket}"

    title = _title_prefix(
        district=district,
        chamber=chamber,
        origin_chamber=origin_chamber,
        existing_title=parsed_title,
    )
    if not composed_name or composed_name == bioguide_id:
        return bioguide_id

    bracket = _compose_bracket(
        party=party,
        state=state,
        district=district,
        title=title,
        existing_bracket=existing_bracket,
    )
    return f"{title} {composed_name} {bracket}"


def format_member_label_from_record(
    *,
    bioguide_id: str,
    full_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    last_name: str | None = None,
    party: str | None = None,
    state: str | None = None,
    district: int | str | None = None,
    chamber: str | None = None,
    origin_chamber: str | None = None,
) -> str:
    """Alias used by sponsorship extraction call sites."""
    return format_congress_member_label(
        bioguide_id=bioguide_id,
        full_name=full_name,
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        party=party,
        state=state,
        district=district,
        chamber=chamber,
        origin_chamber=origin_chamber,
    )


def finalize_graph_member_label(node: Any, *, origin_chamber: str | None = None) -> str:
    """Reformat a graph member node label from accumulated metadata."""
    return format_congress_member_label(
        bioguide_id=node.id,
        full_name=node.label if node.label and node.label != node.id else None,
        party=node.party,
        state=node.state,
        district=node.district,
        chamber=node.chamber,
        origin_chamber=origin_chamber,
    )


def is_canonical_member_label(label: str | None) -> bool:
    """Return True when *label* matches the graph display convention."""
    if not label:
        return False
    return CANONICAL_LABEL_RE.match(label.strip()) is not None


def label_quality_score(label: str | None, *, member_id: str) -> int:
    """Rank label completeness for merge resolution (higher is better)."""
    if not label or label == member_id:
        return 0
    if is_canonical_member_label(label):
        return 2
    return 1


def needs_label_resolution(node: GraphMemberNode) -> bool:
    """Return True when *node* still needs a Member API lookup for its label."""
    if not node.label or node.label == node.id:
        return True
    return not is_canonical_member_label(node.label)


def _member_terms(member: Member) -> list[Term]:
    terms = getattr(member, "terms", None)
    if terms is None:
        return []
    items = getattr(terms, "item", None)
    return list(items or [])


def member_term_for_congress(member: Member, congress: int | None) -> Term | None:
    """Pick the term row for *congress*, falling back to the latest term."""
    terms = _member_terms(member)
    if congress is not None:
        matching = [term for term in terms if getattr(term, "congress", None) == congress]
        if matching:
            return matching[-1]
    return terms[-1] if terms else None


def _term_chamber(term: Term | None) -> str | None:
    if term is None:
        return None
    from .sources import normalize_chamber

    return normalize_chamber(getattr(term, "chamber", None))


def member_to_graph_node(member: Member, *, congress: int | None = None) -> GraphMemberNode | None:
    """Build a graph node from a Congress.gov ``Member`` record."""
    bioguide_id = getattr(member, "bioguideId", None)
    if not bioguide_id:
        return None

    term = member_term_for_congress(member, congress)
    party = normalize_party_code(getattr(term, "partyCode", None) if term else None) or normalize_party_code(
        getattr(member, "partyName", None)
    )
    state = _normalize_state_code(getattr(term, "stateCode", None) if term else None) or _normalize_state_code(
        getattr(member, "state", None)
    )
    district = getattr(term, "district", None) if term else None
    if district is None:
        district = getattr(member, "district", None)
    chamber = _term_chamber(term)

    label = format_congress_member_label(
        bioguide_id=bioguide_id,
        full_name=getattr(member, "invertedOrderName", None) or getattr(member, "directOrderName", None),
        first_name=getattr(member, "firstName", None),
        middle_name=getattr(member, "middleName", None),
        last_name=getattr(member, "lastName", None),
        party=party,
        state=state,
        district=district,
        chamber=chamber,
    )

    return GraphMemberNode(
        id=bioguide_id,
        label=label,
        party=party,
        state=state,
        district=_normalize_district(district),
        chamber=chamber or ("house" if district is not None else None),
    )


class MemberLookupService(Protocol):
    """Minimal member detail protocol used for label enrichment."""

    def get(self, *, bioguide_id: str, client: Any = None, **kwargs: Any) -> Member:
        ...


class MemberLabelResolver:
    """Resolve canonical member labels via cached Member API lookups."""

    def __init__(
        self,
        member_service: MemberLookupService | None,
        *,
        congress: int | None = None,
        client: Any = None,
        registry: dict[str, GraphMemberNode] | None = None,
    ) -> None:
        self._service = member_service
        self._congress = congress
        self._client = client
        self._registry = dict(registry or {})
        self._cache: dict[str, GraphMemberNode] = dict(self._registry)

    def resolve_node(self, bioguide_id: str) -> GraphMemberNode | None:
        """Fetch or recall a member node, using the attached request store when present."""
        if bioguide_id in self._cache:
            cached = self._cache[bioguide_id]
            if not needs_label_resolution(cached):
                return cached
        if self._service is None:
            return self._cache.get(bioguide_id)
        try:
            member = self._service.get(bioguide_id=bioguide_id, client=self._client)
        except Exception:
            return self._cache.get(bioguide_id)
        node = member_to_graph_node(member, congress=self._congress)
        if node is not None:
            self._cache[bioguide_id] = node
        return node

    def enrich_member(self, node: GraphMemberNode) -> GraphMemberNode:
        """Upgrade *node* with a canonical label when possible."""
        if is_canonical_member_label(node.label):
            return node
        resolved = self.resolve_node(node.id)
        if resolved is None:
            node.label = finalize_graph_member_label(node)
            return node
        if label_quality_score(resolved.label, member_id=node.id) > label_quality_score(
            node.label, member_id=node.id
        ):
            node.label = resolved.label
        node.party = node.party or resolved.party
        node.state = node.state or resolved.state
        node.district = node.district or resolved.district
        node.chamber = node.chamber or resolved.chamber
        node.label = finalize_graph_member_label(node)
        return node

    def enrich_members(self, members: dict[str, GraphMemberNode]) -> dict[str, GraphMemberNode]:
        """Enrich every member in *members* in place."""
        for member_id in list(members):
            members[member_id] = self.enrich_member(members[member_id])
        return members

    def enrich_unresolved(self, members: dict[str, GraphMemberNode]) -> int:
        """Resolve labels only for members that still show bioguide IDs or sparse text."""
        updated = 0
        for member_id in list(members):
            node = members[member_id]
            if not needs_label_resolution(node):
                continue
            before = node.label
            members[member_id] = self.enrich_member(node)
            if members[member_id].label != before:
                updated += 1
        return updated

    def seed_registry(self, registry: dict[str, GraphMemberNode]) -> None:
        """Preload seeded roster nodes before incremental enrichment."""
        self._registry.update(registry)
        self._cache.update(registry)


def create_member_label_resolver(
    member_service: MemberLookupService | None,
    *,
    congress: int,
    client: Any = None,
    registry: dict[str, GraphMemberNode] | None = None,
) -> MemberLabelResolver:
    """Factory for graph ingestion/build pipelines."""
    return MemberLabelResolver(
        member_service,
        congress=congress,
        client=client,
        registry=registry,
    )
