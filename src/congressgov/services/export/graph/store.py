"""Persistent congress graph datasets built incrementally from bills."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Protocol

from congressgov.models.entities.bill import Bill
from congressgov.models.entities.member import Member

from .builder import build_graph_slice
from .member_labels import MemberLabelResolver, member_to_graph_node
from .models import (
    BillIngestResult,
    CongressGraphSnapshot,
    GraphExploreConfig,
    GraphMemberNode,
    GraphSlice,
    SponsorshipEvent,
)
from .sources import make_bill_id, sponsorship_events_from_bill


class MemberListService(Protocol):
    """Minimal protocol for listing members in a Congress."""

    def list_by_congress(
        self,
        *,
        congress: int,
        fetch_all: bool = False,
        client: Any = None,
        **kwargs: Any,
    ) -> Any:
        ...


class CongressGraphStore:
    """Persistent member-first graph dataset for one Congress.

    Seed the full member roster once, then add bills over time. Sponsorship
    events and ingested bill IDs are deduplicated so repeat loads are safe.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        congress: int,
        snapshot: CongressGraphSnapshot | None = None,
    ) -> None:
        self.path = Path(path)
        self.congress = congress
        self._snapshot = snapshot or CongressGraphSnapshot(congress=congress)
        if self._snapshot.congress != congress:
            raise ValueError(
                f"Snapshot congress {self._snapshot.congress} does not match store congress {congress}"
            )
        self._event_index: dict[str, SponsorshipEvent] = {
            event.event_id: event for event in self._snapshot.events
        }
        self._bill_ids: set[str] = set(self._snapshot.bill_ids)

    @property
    def members(self) -> dict[str, GraphMemberNode]:
        return self._snapshot.members

    @property
    def events(self) -> list[SponsorshipEvent]:
        return list(self._event_index.values())

    @property
    def bill_ids(self) -> set[str]:
        return set(self._bill_ids)

    @property
    def member_count(self) -> int:
        return len(self._snapshot.members)

    @property
    def event_count(self) -> int:
        return len(self._event_index)

    @property
    def bill_count(self) -> int:
        return len(self._bill_ids)

    @classmethod
    def load(cls, path: str | Path, *, congress: int | None = None) -> CongressGraphStore:
        """Load a persisted dataset from disk."""
        file_path = Path(path)
        if not file_path.exists():
            if congress is None:
                raise FileNotFoundError(f"No graph store found at {file_path}")
            return cls(file_path, congress=congress)

        payload = json.loads(file_path.read_text(encoding="utf-8"))
        snapshot = CongressGraphSnapshot.model_validate(payload)
        resolved_congress = congress if congress is not None else snapshot.congress
        return cls(file_path, congress=resolved_congress, snapshot=snapshot)

    @classmethod
    def open(cls, path: str | Path, *, congress: int) -> CongressGraphStore:
        """Open an existing store or create a new empty dataset."""
        file_path = Path(path)
        if file_path.exists():
            return cls.load(file_path, congress=congress)
        return cls(file_path, congress=congress)

    @classmethod
    def open_for_workspace(
        cls,
        workspace: Any,
        congress: int,
    ) -> CongressGraphStore:
        """Open or create a graph dataset under *workspace* default paths."""
        return cls.open(workspace.paths.graph_path(congress), congress=congress)

    def save(self) -> None:
        """Persist the dataset to disk using an atomic replace."""
        self._snapshot.events = list(self._event_index.values())
        self._snapshot.bill_ids = sorted(self._bill_ids)
        self._snapshot.provenance = {
            "built_at": datetime.now(UTC).isoformat(),
            "schema": "congress_graph/v1",
            "bill_count": len(self._bill_ids),
            "event_count": len(self._event_index),
            "member_count": len(self._snapshot.members),
            "path": str(self.path),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = self._snapshot.model_dump(mode="json")
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_path.replace(self.path)

    def seed_members(self, members: Iterable[Member]) -> int:
        """Add congress members as nodes without removing existing entries."""
        added = 0
        for member in members:
            node = member_to_graph_node(member, congress=self.congress)
            if node is None:
                continue
            if node.id not in self._snapshot.members:
                self._snapshot.members[node.id] = node
                added += 1
        return added

    def seed_members_from_service(
        self,
        member_service: MemberListService,
        *,
        fetch_all: bool = True,
        client: Any = None,
    ) -> int:
        """Fetch and seed the full member roster for this Congress."""
        result = member_service.list_by_congress(
            congress=self.congress,
            fetch_all=fetch_all,
            client=client,
        )
        member_items = getattr(result, "members", None) or []
        return self.seed_members(member_items)

    def add_bill(
        self,
        bill: Bill,
        cosponsors: Any | None = None,
        *,
        save: bool = False,
    ) -> BillIngestResult:
        """Ingest one bill's sponsorship events, skipping duplicates."""
        bill_congress = int(getattr(bill, "congress"))
        if bill_congress != self.congress:
            return BillIngestResult(
                bill_id="",
                added=False,
                skipped_reason=f"bill congress {bill_congress} does not match store congress {self.congress}",
            )

        bill_type = getattr(bill, "bill_type", getattr(bill, "type", None))
        if hasattr(bill_type, "value"):
            bill_type = str(bill_type.value)
        bill_number = getattr(bill, "bill_number", getattr(bill, "number", None))
        bill_id = make_bill_id(bill_congress, str(bill_type).lower(), int(bill_number))

        if bill_id in self._bill_ids:
            return BillIngestResult(
                bill_id=bill_id,
                added=False,
                skipped_reason="already_ingested",
            )

        new_events = sponsorship_events_from_bill(bill, cosponsors)
        if not new_events:
            # A bill with zero cosponsors right now (e.g. cosponsor data
            # wasn't fetched yet, or none exist yet) must NOT be marked as
            # permanently ingested -- otherwise it can never be revisited
            # once cosponsors are added later, since add_bill()/add_bills()
            # both skip anything already in self._bill_ids.
            return BillIngestResult(
                bill_id=bill_id,
                added=False,
                skipped_reason="no_sponsorship_events",
            )

        added_count = 0
        for event in new_events:
            if event.event_id in self._event_index:
                continue
            self._event_index[event.event_id] = event
            added_count += 1

        self._bill_ids.add(bill_id)
        if save:
            self.save()
        return BillIngestResult(bill_id=bill_id, added=True, event_count=added_count)

    def add_bills(
        self,
        bills: Iterable[Bill],
        *,
        fetch_cosponsors: bool = False,
        cosponsor_limit: int = 250,
        save: bool = False,
    ) -> list[BillIngestResult]:
        """Ingest many bills, optionally fetching cosponsors per bill."""
        results: list[BillIngestResult] = []
        for bill in bills:
            bill_congress = int(getattr(bill, "congress"))
            if bill_congress != self.congress:
                results.append(
                    BillIngestResult(
                        bill_id="",
                        added=False,
                        skipped_reason=(
                            f"bill congress {bill_congress} does not match "
                            f"store congress {self.congress}"
                        ),
                    )
                )
                continue

            bill_type = getattr(bill, "bill_type", getattr(bill, "type", None))
            if hasattr(bill_type, "value"):
                bill_type = str(bill_type.value)
            bill_number = getattr(bill, "bill_number", getattr(bill, "number", None))
            bill_id = make_bill_id(bill_congress, str(bill_type).lower(), int(bill_number))

            if bill_id in self._bill_ids:
                results.append(
                    BillIngestResult(
                        bill_id=bill_id,
                        added=False,
                        skipped_reason="already_ingested",
                    )
                )
                continue

            cosponsors = None
            if fetch_cosponsors and hasattr(bill, "get_cosponsors"):
                cosponsors = bill.get_cosponsors(limit=cosponsor_limit)
            results.append(self.add_bill(bill, cosponsors, save=False))
        if save:
            self.save()
        return results

    def resolve_member_labels(
        self,
        member_resolver: MemberLabelResolver,
        *,
        save: bool = False,
    ) -> int:
        """Upgrade persisted roster labels via cached Member API lookups."""
        member_resolver.seed_registry(self._snapshot.members)
        updated = member_resolver.enrich_unresolved(self._snapshot.members)
        if save and updated:
            self.save()
        return updated

    def build_slice(
        self,
        config: GraphExploreConfig,
        *,
        include_all_members: bool | None = None,
        member_resolver: MemberLabelResolver | None = None,
    ) -> GraphSlice:
        """Build a graph projection from the persisted dataset."""
        use_full_roster = (
            config.include_all_members
            if include_all_members is None
            else include_all_members
        )
        explore_config = config.model_copy(
            update={
                "congress": self.congress,
                "include_all_members": use_full_roster,
            }
        )
        member_registry = self._snapshot.members if use_full_roster else None
        return build_graph_slice(
            self.events,
            explore_config,
            member_registry=member_registry,
            member_resolver=member_resolver,
        )

    def stats(self) -> dict[str, int]:
        """Return basic dataset counters."""
        return {
            "congress": self.congress,
            "memberCount": self.member_count,
            "eventCount": self.event_count,
            "billCount": self.bill_count,
        }
