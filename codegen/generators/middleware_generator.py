"""
Middleware Generator for service classes.

This module generates middleware service classes that wrap the API client
and provide high-level interfaces for working with Congressional data.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_generator import BaseGenerator, GenerationResult
from ..processors.spec_parser import EndpointConfig, EntityConfig

logger = logging.getLogger(__name__)


class MiddlewareGenerator(BaseGenerator):
    """
    Generator for middleware service classes.
    
    This generator:
    - Creates service classes that wrap API client calls
    - Generates expansion mappings and parameter mappings
    - Provides high-level interfaces for entity operations
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        spec_parser: Any,
        file_manager: Optional[Any] = None,
        template_engine: Optional[Any] = None,
        code_formatter: Optional[Any] = None
    ):
        """Initialize MiddlewareGenerator."""
        super().__init__(config, spec_parser, file_manager, template_engine, code_formatter)
        self.middleware_config = config.get('middleware', {})
    
    def generate(self) -> GenerationResult:
        """Generate middleware service classes."""
        self.logger.info("Starting middleware generation...")
        
        try:
            errors = self.validate_generation_prerequisites()
            if errors:
                return self.create_generation_result(
                    success=False,
                    generated_files=[],
                    errors=errors,
                    summary="Middleware generation failed validation"
                )
            
            processing_order = self.get_processing_order()
            generated_files = []
            all_errors = []
            
            for entity_name in processing_order:
                try:
                    written = self._generate_service_file(entity_name)
                    for service_file in written:
                        generated_files.append(service_file)
                        self.logger.info(f"Generated middleware for entity: {entity_name}")
                except Exception as e:
                    error_msg = f"Failed to generate middleware for entity {entity_name}: {e}"
                    self.logger.error(error_msg)
                    all_errors.append(error_msg)
            
            success = len(all_errors) == 0
            summary = f"Generated {len(generated_files)} middleware files"
            if all_errors:
                summary += f" with {len(all_errors)} errors"
            
            return self.create_generation_result(
                success=success,
                generated_files=generated_files,
                errors=all_errors,
                summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"Middleware generation failed: {e}")
            return self.create_generation_result(
                success=False,
                generated_files=[],
                errors=[str(e)],
                summary="Middleware generation failed with exception"
            )
    
    def get_required_config_keys(self) -> List[str]:
        """Get required configuration keys."""
        return ['output', 'middleware']
    
    def _to_async_api_function(self, sync_name: str) -> str:
        """Map compat sync export name to async export (e.g. bill_details_sync -> bill_details_async)."""
        if sync_name.endswith("_sync"):
            return f"{sync_name[:-5]}_async"
        if sync_name.endswith("_async"):
            return sync_name
        return f"{sync_name}_async"

    def _generate_service_file(self, entity_name: str) -> List[Path]:
        """Generate sync and async middleware for an entity (skips protected hand modules)."""
        entity_config = self.get_entity_config(entity_name)
        if not entity_config:
            return []

        middleware_dir = self.get_output_directory('middleware')
        service_path = entity_config.model_config.service_path or ""
        if service_path and "." in service_path:
            service_stem = service_path.rsplit(".", 1)[-1]
        else:
            service_stem = self._api_package_name(entity_config)

        if service_stem == "actions":
            self.logger.info(
                "Skipping middleware service for %s (extension-only; no hand actions.py)",
                entity_name,
            )
            return []

        output_path = middleware_dir / f"{service_stem}.py"
        async_output = middleware_dir / "async_api" / f"{service_stem}.py"
        if self._should_skip_protected_generation(output_path) and self._should_skip_protected_generation(
            async_output
        ):
            return []

        written: List[Path] = []
        write_path = self._review_sidecar_path(output_path)
        if not self._should_skip_protected_generation(output_path):
            context = self._prepare_service_context(entity_config)
            self.render_template('service.py.jinja2', context, write_path)
            if write_path != output_path:
                self.logger.info(
                    "Wrote review sidecar %s (hand-maintained %s is protected)",
                    write_path,
                    output_path,
                )
            written.append(write_path)

        if not self._should_skip_protected_generation(async_output):
            async_write = (
                async_output.with_name(f"{service_stem}.generated.py")
                if self._emit_review_sidecars() and self.file_manager.is_protected(async_output)
                else async_output
            )
            async_context = self._prepare_async_service_context(
                entity_config, self._prepare_service_context(entity_config)
            )
            self.render_template('service_async.py.jinja2', async_context, async_write)
            if async_write != async_output:
                self.logger.info(
                    "Wrote async review sidecar %s (hand-maintained %s is protected)",
                    async_write,
                    async_output,
                )
            written.append(async_write)
        return written

    def _prepare_async_service_context(
        self, entity_config: EntityConfig, sync_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Async template context: Async* class name and *_async API imports."""
        async_context = dict(sync_context)
        async_context["async_service_name"] = f"Async{entity_config.name}"
        async_context["api_functions"] = [
            self._to_async_api_function(f) for f in sync_context["api_functions"]
        ]
        for prefix in ("primary_endpoint", "search_endpoint"):
            key = f"{prefix}_api_function"
            if async_context.get(prefix) and async_context.get(key):
                async_context[key] = self._to_async_api_function(async_context[key])
        if entity_config.expansion_mappings:
            async_context["async_mappings_dict_name"] = f"ASYNC_{entity_config.name.upper()}_MAPPINGS"
        else:
            async_context["async_mappings_dict_name"] = None
        return async_context
    
    def _format_params_signature(self, params: List[str]) -> str:
        if not params:
            return ""
        return ",\n        ".join(f"{p}: Any" for p in params)

    def _format_params_example(self, params: List[str]) -> str:
        if not params:
            return ""
        return ", ".join(f"{p}=..." for p in params)

    def _endpoint_template_fields(
        self, endpoint: Optional[EndpointConfig], *, is_primary: bool
    ) -> Dict[str, Any]:
        if not endpoint:
            flag = "primary_endpoint" if is_primary else "search_endpoint"
            return {flag: False}
        params = endpoint.python_params
        prefix = "primary_endpoint" if is_primary else "search_endpoint"
        return {
            ("primary_endpoint" if is_primary else "search_endpoint"): True,
            f"{prefix}_api_function": endpoint.api_function,
            f"{prefix}_params": self._format_params_signature(params),
            f"{prefix}_params_list": params,
            f"{prefix}_example_params": self._format_params_example(params),
        }

    def _prepare_service_context(self, entity_config: EntityConfig) -> Dict[str, Any]:
        """Prepare template context for service generation."""
        api_functions: List[str] = []
        if entity_config.primary_endpoint:
            api_functions.append(entity_config.primary_endpoint.api_function)
        if entity_config.list_endpoint:
            api_functions.append(entity_config.list_endpoint.api_function)
        for expansion_mapping in entity_config.expansion_mappings.values():
            api_functions.append(expansion_mapping.api_function)
        api_functions = list(dict.fromkeys(api_functions))

        hooks = entity_config.service_codegen or {}
        registry_models = hooks.get("registry_models") or []

        context: Dict[str, Any] = {
            'service_name': entity_config.name,
            'entity_name': entity_config.name,
            'model_name': entity_config.name,
            'collection_name': entity_config.model_config.collection_class,
            'entity_description': f"{entity_config.name} data from the Congress.gov API",
            'entity_path': self._api_package_name(entity_config),
            'api_functions': api_functions,
            'service_hooks': hooks,
            'registry_models': registry_models,
            'mappings_dict_name': f"{entity_config.name.upper()}_MAPPINGS",
            'parameters_dict_name': f"{entity_config.name.upper()}_PARAMETERS",
            'mappings_dict': self._generate_mappings_dict(entity_config),
            'parameters_dict': self._generate_parameters_dict(entity_config),
            'expansion_mappings': entity_config.expansion_mappings,
            'parameter_mappings': entity_config.parameter_mappings,
            'field_mappings': entity_config.field_mappings,
            'extension_path': entity_config.model_config.extension_path,
            'primary_endpoint': False,
            'search_endpoint': False,
        }
        context.update(self._endpoint_template_fields(entity_config.primary_endpoint, is_primary=True))
        context.update(self._endpoint_template_fields(entity_config.list_endpoint, is_primary=False))
        return context

    def _api_package_name(self, entity_config: EntityConfig) -> str:
        """OpenAPI client package folder (e.g. Amendment -> amendments)."""
        packages = {
            "Bill": "bill",
            "Amendment": "amendments",
            "Member": "member",
            "Committee": "committee",
            "Hearing": "hearing",
            "Nomination": "nomination",
            "Treaty": "treaty",
            "HouseVote": "house_vote",
            "Summaries": "summaries",
            "CRSReport": "crsreport",
            "HouseCommunication": "house_communication",
            "SenateCommunication": "senate_communication",
            "CommitteeMeeting": "committee_meeting",
            "CommitteeReport": "committee_report",
            "CommitteePrint": "committee_print",
            "Congress": "congress",
            "HouseRequirement": "house_requirement",
            "CongressionalRecord": "congressional_record",
            "DailyCongressionalRecord": "daily_congressional_record",
            "BoundCongressionalRecord": "bound_congressional_record",
            "Actions": "bill",
        }
        return packages.get(entity_config.name, entity_config.name.lower())
    
    def _generate_mappings_dict(self, entity_config: EntityConfig) -> str:
        """Generate mappings dictionary code."""
        lines = []
        lines.append(f"{entity_config.name.upper()}_MAPPINGS = {{")
        
        for attr_name, expansion_mapping in entity_config.expansion_mappings.items():
            api_fn = getattr(
                expansion_mapping.api_function,
                "__name__",
                repr(expansion_mapping.api_function),
            )
            lines.append(
                '    "'
                + attr_name
                + '": {'
                + api_fn
                + ": "
                + expansion_mapping.model
                + "Model},"
            )
        
        lines.append("}")
        return "\n".join(lines)
    
    def _generate_parameters_dict(self, entity_config: EntityConfig) -> str:
        """Generate parameters dictionary code."""
        lines = []
        lines.append(f"{entity_config.name.upper()}_PARAMETERS = {{")
        
        for param_name, mapping_data in entity_config.parameter_mappings.items():
            if isinstance(mapping_data, list):
                lines.append(f'    "{param_name}": {mapping_data},')
            else:
                lines.append(f'    "{param_name}": {mapping_data!r},')
        
        lines.append("}")
        return "\n".join(lines)
