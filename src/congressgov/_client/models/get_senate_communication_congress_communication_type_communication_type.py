from enum import Enum


class GetSenateCommunicationCongressCommunicationTypeCommunicationType(str, Enum):
    EC = "ec"
    PM = "pm"
    POM = "pom"

    def __str__(self) -> str:
        return str(self.value)
