from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService
from congressgov.services.core.validation import validate_congress

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.committee_report import (
    committee_report_details_sync,
    committee_report_id_text_sync,
)

from congressgov.models.base.model import ApiEnvelope
from congressgov.models.documents.committee_report import CommitteeReportTexts

CommitteeReportModel = ModelRegistry.get_model("CommitteeReport")
CommitteeReportsModel = ModelRegistry.get_model("CommitteeReports")
CommitteeReportTextModel = ModelRegistry.get_model("CommitteeReportText")

COMMITTEE_REPORT_MAPPINGS = {
    "text": {committee_report_id_text_sync: CommitteeReportTexts},
}

COMMITTEE_REPORT_PARAMETERS = {
    "congress": "congress",
    "report_type": ["report_type", "reportType", "type"],
    "report_number": ["report_number", "reportNumber", "number"],
}

__all__ = [
    "CommitteeReport",
    "COMMITTEE_REPORT_MAPPINGS",
    "COMMITTEE_REPORT_PARAMETERS",
]


class CommitteeReport(ApiService):
    """CommitteeReport service provides API access for committee report data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        report_type: str,
        report_number: int,
        format_: str = None
    ) -> CommitteeReportModel:
        """Get detailed information about a specific committee report."""
        # CUSTOM: validation
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = committee_report_details_sync(
            client=client,
            congress=congress,
            report_type=report_type,
            report_number=report_number,
            format_=format_
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CommitteeReportModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def get_text(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int,
        report_type: str,
        report_number: int,
        format_: str = None,
    ):
        """Return text versions for a committee report."""
        # CUSTOM: committee report text sub-endpoint
        validate_congress(congress)

        client = ApiService._resolve_client(self, client)
        response = committee_report_id_text_sync(
            client=client,
            congress=congress,
            report_type=report_type,
            report_number=report_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        payload = response_json.get("data", api_envelope.data)
        if isinstance(payload, list):
            return [CommitteeReportTextModel.model_validate(item) for item in payload]
        return CommitteeReportTextModel.model_validate(payload)

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        congress: int = None,
        report_type: str = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ) -> CommitteeReportsModel:
        """Search for committee reports using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'committee-report',
            self,
            client=client,
            congress=congress,
            report_type=report_type,
            format_=format_,
            offset=offset,
            limit=limit
        )
