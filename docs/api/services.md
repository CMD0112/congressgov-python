# Services

Each class below wraps one Congress.gov resource: a `get()` for the detail endpoint, a `search()`
for the list endpoint, and (where the API supports it) sub-resource getters like `get_actions()` or
`get_cosponsors()`. See [REFERENCE.md](../guide/REFERENCE.md) for the typical `get()` identifiers per
service, and [MEMBERS_QUERY.md](../guide/MEMBERS_QUERY.md) for the `Members` collection's query helpers.

## Bill

::: congressgov.services.bill.Bill

## Amendment

::: congressgov.services.amendment.Amendment

## Member

::: congressgov.services.member.Member

## Committee

::: congressgov.services.committee.Committee

## CommitteeMeeting

::: congressgov.services.committee_meeting.CommitteeMeeting

## CommitteePrint

::: congressgov.services.committee_print.CommitteePrint

## CommitteeReport

::: congressgov.services.committee_report.CommitteeReport

## Congress

::: congressgov.services.congress.Congress

## CongressionalRecord

::: congressgov.services.congressional_record.CongressionalRecord

## DailyCongressionalRecord

::: congressgov.services.daily_congressional_record.DailyCongressionalRecord

## BoundCongressionalRecord

::: congressgov.services.bound_congressional_record.BoundCongressionalRecord

## CRSReport

::: congressgov.services.crsreport.CRSReport

## Hearing

::: congressgov.services.hearing.Hearing

## HouseCommunication

::: congressgov.services.house_communication.HouseCommunication

## HouseRequirement

::: congressgov.services.house_requirement.HouseRequirement

## HouseVote

::: congressgov.services.house_vote.HouseVote

## Nomination

::: congressgov.services.nomination.Nomination

## SenateCommunication

::: congressgov.services.senate_communication.SenateCommunication

## Summaries

::: congressgov.services.summaries.Summaries

## Treaty

::: congressgov.services.treaty.Treaty
