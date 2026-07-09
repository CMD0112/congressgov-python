from enum import Enum


class GetCommitteeReportCongressReportTypeReportNumberTextReportType(str, Enum):
    ERPT = "erpt"
    HRPT = "hrpt"
    SRPT = "srpt"

    def __str__(self) -> str:
        return str(self.value)
