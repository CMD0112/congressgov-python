from enum import Enum


class GetCommitteeMeetingCongressChamberEventIdChamber(str, Enum):
    HOUSE = "house"
    JOINT = "joint"
    SENATE = "senate"

    def __str__(self) -> str:
        return str(self.value)
