from enum import Enum


class GetAmendmentCongressAmendmentTypeAmendmentNumberCosponsorsFormat(str, Enum):
    JSON = "json"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
