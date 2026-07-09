from __future__ import annotations
from datetime import date
from ..base.model import Model
from ..base.types import URL
from ..base.enums import LegislationType, AmendmentType, VoteResult, VoteType, VoteQuestion


class HouseVote(Model):
    startDate: date | str | None = None
    updateDate: date | str | None = None
    identifier: str | int | None = None
    congress: int | None = None
    sessionNumber: int | None = None
    rollCallNumber: int | None = None
    voteType: VoteType | None = None
    result: VoteResult | str | None = None
    legislationType: LegislationType | None = None
    legislationNumber: int | None = None
    voteQuestion: VoteQuestion | str | None = None  # ?: Is enum useful here? Could just be str
    amendmentType: AmendmentType | str | None = None  # ?: Is enum useful here? Could just be str
    amendmentNumber: int | None = None
    amendmentAuthor: str | None = None   # ?: Should this use a Members object?
    votePartyTotal: list[dict[str, str | int | dict]] | None = None
    legislationUrl: URL | str | None = None


# HouseVote.model_rebuild()  # Handled by centralized rebuild system


class HouseVotes(Model):
    houseRollCallVotes: list[HouseVote] | None = None


# HouseVotes.model_rebuild()  # Handled by centralized rebuild system


class MemberVotes(Model):
    startDate: date | str | None = None
    updateDate: date | str | None = None
    identifier: str | int | None = None
    congress: int | None = None
    sessionNumber: int | None = None
    rollCallNumber: int | None = None
    voteType: VoteType | None = None
    result: VoteResult | str | None = None
    legislationType: LegislationType | None = None
    legislationNumber: int | None = None
    voteQuestion: VoteQuestion | str | None = None  # ?: Is enum useful here? Could just be str
    amendmentType: AmendmentType | str | None = None  # ?: Is enum useful here? Could just be str
    amendmentNumber: int | None = None
    amendmentAuthor: str | None = None   # ?: Should this use a Members object?
    results: list[dict[str, str | int]] | None = None


# MemberVotes.model_rebuild()  # Handled by centralized rebuild system

# OpenAPI / client schema name alias
HouseVoteMembers = MemberVotes
