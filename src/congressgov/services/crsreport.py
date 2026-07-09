from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.api_service import ApiService

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.crsreport import crsreport_details_sync

from congressgov.models.base.model import ApiEnvelope

CRSReportModel = ModelRegistry.get_model("CRSReport")

CRS_REPORT_MAPPINGS = {}

__all__ = ['CRSReport', 'CRS_REPORT_MAPPINGS']


class CRSReport(ApiService):
    """CRSReport service provides API access for CRS report data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        report_number: str,
        format_: str = None
    ) -> CRSReportModel:
        """Get detailed information about a specific CRS report."""
        client = ApiService._resolve_client(self, client)
        response = crsreport_details_sync(
            client=client,
            report_number=report_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CRSReportModel.model_validate(api_envelope.data)
        result.client = client
        self._last_result = result
        return result

    def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ):
        """Search for CRS reports using the universal search system."""
        from congressgov.services.core.search import search as universal_search

        # CUSTOM: universal search delegation
        return universal_search(
            'crs-report',
            self,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit
        )
