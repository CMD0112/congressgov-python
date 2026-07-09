"""Synthetic sponsorship datasets for graph stress testing."""

from __future__ import annotations

import random
from itertools import count

from .member_labels import format_congress_member_label
from .models import SponsorshipEvent
from .sources import make_bill_id, make_event_id


def generate_dense_sponsorship_events(
    *,
    member_count: int = 120,
    bills_per_sponsor: int = 25,
    cosponsors_per_bill: int = 40,
    congress: int = 118,
    bill_type: str = "hr",
    seed: int = 42,
) -> list[SponsorshipEvent]:
    """Generate a highly connected synthetic sponsor/cosponsor event set.

    Each sponsor introduces multiple bills; each bill receives many cosponsors.
    Useful for stress-testing layouts, truncation, and renderers without API calls.
    """
    if member_count < 2:
        raise ValueError("member_count must be at least 2")

    rng = random.Random(seed)
    parties = ["D", "R"]
    states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]
    member_ids = [f"M{index:04d}" for index in range(member_count)]
    bill_counter = count(1)
    events: list[SponsorshipEvent] = []

    for sponsor_index, sponsor_id in enumerate(member_ids):
        sponsor_party = parties[sponsor_index % len(parties)]
        sponsor_state = states[sponsor_index % len(states)]
        for _ in range(bills_per_sponsor):
            bill_number = next(bill_counter)
            bill_id = make_bill_id(congress, bill_type, bill_number)
            cosponsor_pool = [member_id for member_id in member_ids if member_id != sponsor_id]
            rng.shuffle(cosponsor_pool)
            selected_cosponsors = cosponsor_pool[: min(cosponsors_per_bill, len(cosponsor_pool))]

            for cosponsor_index, cosponsor_id in enumerate(selected_cosponsors):
                cosponsor_party = parties[(sponsor_index + cosponsor_index + 1) % len(parties)]
                cosponsor_state = states[(sponsor_index + cosponsor_index) % len(states)]
                sponsor_name = format_congress_member_label(
                    bioguide_id=sponsor_id,
                    full_name=f"Rep. Member {sponsor_id}",
                    party=sponsor_party,
                    state=sponsor_state,
                    district=(sponsor_index % 53) + 1,
                    origin_chamber="house",
                )
                cosponsor_name = format_congress_member_label(
                    bioguide_id=cosponsor_id,
                    full_name=f"Rep. Member {cosponsor_id}",
                    party=cosponsor_party,
                    state=cosponsor_state,
                    district=(cosponsor_index % 53) + 1,
                    origin_chamber="house",
                )
                events.append(
                    SponsorshipEvent(
                        event_id=make_event_id(bill_id, sponsor_id, cosponsor_id),
                        bill_id=bill_id,
                        congress=congress,
                        bill_type=bill_type,
                        bill_number=bill_number,
                        bill_title=f"Synthetic Bill {bill_number}",
                        origin_chamber="house",
                        policy_area="Health",
                        sponsor_bioguide_id=sponsor_id,
                        sponsor_name=sponsor_name,
                        sponsor_party=sponsor_party,
                        sponsor_state=sponsor_state,
                        sponsor_district=(sponsor_index % 53) + 1,
                        cosponsor_bioguide_id=cosponsor_id,
                        cosponsor_name=cosponsor_name,
                        cosponsor_party=cosponsor_party,
                        cosponsor_state=cosponsor_state,
                        cosponsor_district=(cosponsor_index % 53) + 1,
                        is_original_cosponsor=cosponsor_index < 5,
                        is_active=True,
                    )
                )
    return events
