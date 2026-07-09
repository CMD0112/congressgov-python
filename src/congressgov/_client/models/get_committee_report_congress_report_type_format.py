from enum import Enum


class GetCommitteeReportCongressReportTypeFormat(str, Enum):
    JSON = "json"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
