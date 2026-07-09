from enum import Enum


class GetHouseCommunicationCongressCommunicationTypeCommunicationNumberCommunicationType(str, Enum):
    EC = "ec"
    ML = "ml"
    PM = "pm"
    PT = "pt"

    def __str__(self) -> str:
        return str(self.value)
