from enum import Enum


class GetTreatyCongressTreatyNumberTreatySuffixFormat(str, Enum):
    JSON = "json"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
