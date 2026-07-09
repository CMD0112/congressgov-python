from __future__ import annotations
import json
from typing import TYPE_CHECKING
from congressgov.services.core.async_api_service import AsyncApiService
from congressgov.services.core.model_registry import ModelRegistry
from congressgov._client.api.crsreport import crsreport_details_async
from congressgov.models.base.model import ApiEnvelope

if TYPE_CHECKING:
    from congressgov._client import AuthenticatedClient

CRSReportModel = ModelRegistry.get_model("CRSReport")

ASYNC_CRS_REPORT_MAPPINGS = {}

__all__ = ['AsyncCRSReport', 'ASYNC_CRS_REPORT_MAPPINGS']


class AsyncCRSReport(AsyncApiService):
    """CRSReport service provides API access for CRS report data."""
    
    def __init__(self, client: AuthenticatedClient | None = None):
        self.client = client
        self._last_result = None

    async def get(
        self,
        *,
        client: AuthenticatedClient | None = None,
        report_number: str,
        format_: str = None,
    ) -> CRSReportModel:
        resolved_client = await AsyncApiService._resolve_client(self, client)
        response = await crsreport_details_async(
            client=resolved_client,
            report_number=report_number,
            format_=format_,
        )
        response_json = json.loads(response.content)
        api_envelope = ApiEnvelope.model_validate(response_json)
        result = CRSReportModel.model_validate(api_envelope.data)
        result.client = resolved_client
        self._last_result = result
        return result

    async def search(
        self,
        *,
        client: AuthenticatedClient | None = None,
        format_: str = None,
        offset: int = None,
        limit: int = None
    ):
        """Search for CRS reports using the universal search system."""
        from congressgov.services.core.search import search_async as universal_search
        
        return await universal_search(
            'crs-report',
            self,
            client=client,
            format_=format_,
            offset=offset,
            limit=limit
        )
