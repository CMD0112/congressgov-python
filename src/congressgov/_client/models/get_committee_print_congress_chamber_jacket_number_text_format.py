from enum import Enum


class GetCommitteePrintCongressChamberJacketNumberTextFormat(str, Enum):
    JSON = "json"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
