"""
Main orchestration module for the code generation system.

This module coordinates the entire code generation pipeline including
API client generation, model generation, middleware generation, and
extension generation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List

from .generators.api_client_generator import ApiClientGenerator
from .generators.model_generator import ModelGenerator
from .generators.middleware_generator import MiddlewareGenerator
from .generators.extension_generator import ExtensionGenerator
from .generators.registry_generator import RegistryGenerator
from .processors.spec_parser import SpecParser
from .utils.file_manager import FileManager
from .utils.template_engine import TemplateEngine
from .utils.code_formatter import CodeFormatter
from .generators.base_generator import GenerationResult

logger = logging.getLogger(__name__)


class CodeGenerationSystem:
    """
    Main orchestration class for the code generation system.
    
    This class coordinates the entire code generation pipeline:
    1. Parse OpenAPI specification with custom annotations
    2. Generate API client using openapi-python-client
    3. Generate Pydantic models from schemas
    4. Generate middleware service classes
    5. Generate extension methods
    6. Generate model registry
    7. Format generated code
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CodeGenerationSystem.
        
        Args:
            config: Configuration dictionary for the generation system
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        generation = config.get("generation", {})
        # Initialize components
        self.file_manager = FileManager(
            backup_suffix=generation.get("backup_suffix", ".backup"),
            custom_marker=generation.get("custom_marker", "# CUSTOM:"),
            generated_marker=generation.get("generated_marker", "# GENERATED:"),
            create_backups=generation.get("backup", True),
            protected_paths=config.get("protected_paths", []),
        )
        self.template_engine = TemplateEngine(
            template_dirs=[Path(__file__).parent / "templates"]
        )
        self.code_formatter = CodeFormatter()
        self.spec_parser = SpecParser()
        
        # Initialize generators
        self.api_client_generator = ApiClientGenerator(
            config, self.spec_parser, self.file_manager, self.template_engine, self.code_formatter
        )
        self.model_generator = ModelGenerator(
            config, self.spec_parser, self.file_manager, self.template_engine, self.code_formatter
        )
        self.middleware_generator = MiddlewareGenerator(
            config, self.spec_parser, self.file_manager, self.template_engine, self.code_formatter
        )
        self.extension_generator = ExtensionGenerator(
            config, self.spec_parser, self.file_manager, self.template_engine, self.code_formatter
        )
        self.registry_generator = RegistryGenerator(
            config, self.spec_parser, self.file_manager, self.template_engine, self.code_formatter
        )
        
        self.logger.info("CodeGenerationSystem initialized")

    def _apply_entity_mapping_fallback(self) -> None:
        em_cfg = self.config.get("entity_mappings", {})
        if em_cfg.get("use_as_fallback"):
            mappings_path = Path(
                em_cfg.get("path", "codegen/config/entity_mappings.yaml")
            )
            self.spec_parser.apply_entity_mapping_fallback(mappings_path)

    def prepare_spec(self, spec_path: str) -> None:
        """Load OpenAPI spec and entity mappings for single-step generators."""
        self.spec_parser.load_spec(spec_path)
        self.spec_parser.parse_entities()
        self._apply_entity_mapping_fallback()
    
    def generate_all(self, spec_path: str) -> GenerationResult:
        """
        Generate entire project from OpenAPI specification.
        
        Args:
            spec_path: Path to OpenAPI specification file
            
        Returns:
            GenerationResult with overall success status and details
        """
        self.logger.info("Starting full project generation...")
        
        try:
            # Load and parse OpenAPI specification
            self.logger.info(f"Loading OpenAPI specification: {spec_path}")
            self.spec_parser.load_spec(spec_path)
            entities = self.spec_parser.parse_entities()
            self._apply_entity_mapping_fallback()
            
            if not entities:
                return GenerationResult(
                    success=False,
                    generated_files=[],
                    errors=["No entities found in OpenAPI specification"],
                    warnings=[],
                    summary="No entities to generate"
                )
            
            self.logger.info(f"Found {len(entities)} entities: {list(entities.keys())}")
            
            # Validate configuration
            validation_errors = self.spec_parser.validate_configuration()
            if validation_errors:
                self.logger.warning(f"Configuration validation found {len(validation_errors)} errors")
            
            all_generated_files = []
            all_errors = []
            all_warnings = []
            
            # Step 1: Generate API client
            self.logger.info("Step 1: Generating API client...")
            client_result = self.generate_api_client(spec_path)
            all_generated_files.extend(client_result.generated_files)
            all_errors.extend(client_result.errors)
            all_warnings.extend(client_result.warnings)
            
            if not client_result.success:
                self.logger.error("API client generation failed, stopping pipeline")
                return GenerationResult(
                    success=False,
                    generated_files=all_generated_files,
                    errors=all_errors,
                    warnings=all_warnings,
                    summary="Generation failed at API client step"
                )
            
            # Step 2: Generate models
            self.logger.info("Step 2: Generating models...")
            models_result = self.generate_models(spec_path)
            all_generated_files.extend(models_result.generated_files)
            all_errors.extend(models_result.errors)
            all_warnings.extend(models_result.warnings)
            
            if not models_result.success:
                self.logger.error("Model generation failed, stopping pipeline")
                return GenerationResult(
                    success=False,
                    generated_files=all_generated_files,
                    errors=all_errors,
                    warnings=all_warnings,
                    summary="Generation failed at model step"
                )
            
            # Step 3: Generate middleware
            self.logger.info("Step 3: Generating middleware...")
            middleware_result = self.generate_middleware(spec_path)
            all_generated_files.extend(middleware_result.generated_files)
            all_errors.extend(middleware_result.errors)
            all_warnings.extend(middleware_result.warnings)
            
            # Step 4: Generate extensions
            self.logger.info("Step 4: Generating extensions...")
            extensions_result = self.generate_extensions(spec_path)
            all_generated_files.extend(extensions_result.generated_files)
            all_errors.extend(extensions_result.errors)
            all_warnings.extend(extensions_result.warnings)
            
            # Step 5: Generate registry
            self.logger.info("Step 5: Generating registry...")
            registry_result = self.generate_registry(spec_path)
            all_generated_files.extend(registry_result.generated_files)
            all_errors.extend(registry_result.errors)
            all_warnings.extend(registry_result.warnings)

            # Step 6: Generate URL route table
            self.logger.info("Step 6: Generating URL routes...")
            url_routes_result = self.generate_url_routes()
            all_generated_files.extend(url_routes_result.generated_files)
            all_errors.extend(url_routes_result.errors)
            all_warnings.extend(url_routes_result.warnings)
            
            # Determine overall success
            success = all([
                client_result.success,
                models_result.success,
                middleware_result.success,
                extensions_result.success,
                registry_result.success,
                url_routes_result.success,
            ])
            
            summary = f"Generated {len(all_generated_files)} files across all components"
            if all_errors:
                summary += f" with {len(all_errors)} errors"
            
            self.logger.info(f"Full project generation completed: {summary}")
            
            return GenerationResult(
                success=success,
                generated_files=all_generated_files,
                errors=all_errors,
                warnings=all_warnings,
                summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"Full project generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="Generation failed with exception"
            )
    
    def generate_api_client(self, spec_path: str) -> GenerationResult:
        """Generate API client using openapi-python-client."""
        try:
            self.spec_parser.load_spec(spec_path)
            self.spec_parser.parse_entities()
            self._apply_entity_mapping_fallback()

            # Add spec path to config for the generator
            self.api_client_generator.config['spec_path'] = spec_path
            
            result = self.api_client_generator.generate()
            if not result.success:
                return result

            self._normalize_client_tree()
            self._patch_client_parse_responses()
            self._patch_client_null_datetimes()
            self._patch_client_format_none()

            compat_errors = self._emit_client_compat()
            if compat_errors:
                result.warnings.extend(compat_errors)
                result.errors.extend(compat_errors)
                result.success = False
                result.summary = (
                    f"{result.summary}; client compat failed"
                    if result.summary
                    else "Client compat emission failed"
                )
            return result
        except Exception as e:
            self.logger.error(f"API client generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="API client generation failed"
            )
    
    def _normalize_client_tree(self) -> None:
        """Deterministic isort/ruff on promoted client before compat emission."""
        try:
            from .scripts.normalize_client_tree import normalize_client_imports

            client_root = Path(
                self.config.get("output", {}).get("api_client", "src/congressgov/_client")
            )
            normalize_client_imports(client_root)
        except Exception as exc:
            self.logger.warning("Client tree normalization failed: %s", exc)

    def _patch_client_parse_responses(self) -> None:
        """Fix envelope endpoints where openapi-python-client emits list parsers."""
        try:
            from .scripts.patch_client_parse_response import patch_all_envelope_parsers

            client_root = Path(
                self.config.get("output", {}).get("api_client", "src/congressgov/_client")
            )
            patched = patch_all_envelope_parsers(client_root)
            if patched:
                self.logger.info(
                    "Patched %s client module(s) for envelope list parsers",
                    len(patched),
                )
        except Exception as exc:
            self.logger.warning("Client parse-response patch failed: %s", exc)

    def _patch_client_null_datetimes(self) -> None:
        """Treat JSON null date fields as UNSET before isoparse in generated models."""
        try:
            from .scripts.patch_client_null_datetimes import patch_null_datetime_fields

            client_root = Path(
                self.config.get("output", {}).get("api_client", "src/congressgov/_client")
            )
            patched = patch_null_datetime_fields(client_root)
            if patched:
                self.logger.info(
                    "Patched %s client model(s) for null datetimes",
                    len(patched),
                )
        except Exception as exc:
            self.logger.warning("Client null-datetime patch failed: %s", exc)

    def _patch_client_format_none(self) -> None:
        """Coerce format_=None/str in generated _get_kwargs to JSON enums."""
        try:
            from .scripts.patch_client_format_none import patch_all_client_format_kwargs

            client_root = Path(
                self.config.get("output", {}).get("api_client", "src/congressgov/_client")
            )
            patched = patch_all_client_format_kwargs(client_root)
            if patched:
                self.logger.info(
                    "Patched %s client module(s) for format_=None",
                    len(patched),
                )
        except Exception as exc:
            self.logger.warning("Client format_=None patch failed: %s", exc)

    def _emit_client_compat(self) -> list[str]:
        """Rebuild api/*/__init__.py legacy *_sync exports after client regen."""
        try:
            from .scripts.emit_client_compat import emit_compat
            from .scripts.normalize_client_tree import normalize_client_imports

            client_root = Path(
                self.config.get("output", {}).get("api_client", "src/congressgov/_client")
            )
            aliases_path = Path(__file__).parent / "config" / "legacy_client_aliases.yaml"
            allow_unmatched = self.config.get("client_compat", {}).get("allow_unmatched", False)
            exit_code = emit_compat(
                client_root, aliases_path, allow_unmatched=allow_unmatched
            )
            if exit_code != 0:
                return ["emit_client_compat reported unmatched legacy aliases"]
            normalize_client_imports(client_root)
            return []
        except Exception as exc:
            return [f"emit_client_compat failed: {exc}"]

    def generate_models(self, spec_path: str) -> GenerationResult:
        """Generate Pydantic models from schemas."""
        try:
            return self.model_generator.generate()
        except Exception as e:
            self.logger.error(f"Model generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="Model generation failed"
            )
    
    def generate_middleware(self, spec_path: str) -> GenerationResult:
        """Generate middleware service classes."""
        try:
            return self.middleware_generator.generate()
        except Exception as e:
            self.logger.error(f"Middleware generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="Middleware generation failed"
            )
    
    def generate_extensions(self, spec_path: str) -> GenerationResult:
        """Generate extension methods for models."""
        try:
            return self.extension_generator.generate()
        except Exception as e:
            self.logger.error(f"Extension generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="Extension generation failed"
            )
    
    def generate_registry(self, spec_path: str) -> GenerationResult:
        """Generate model registry."""
        try:
            return self.registry_generator.generate()
        except Exception as e:
            self.logger.error(f"Registry generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="Registry generation failed"
            )

    def generate_url_routes(self) -> GenerationResult:
        """Generate URL route table for fetch_from_url."""
        try:
            from codegen.scripts.generate_url_routes import (
                DEFAULT_ALIASES,
                DEFAULT_OUTPUT,
                load_routes,
                render,
            )

            routes = load_routes(DEFAULT_ALIASES)
            DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            DEFAULT_OUTPUT.write_text(render(routes), encoding="utf-8")
            return GenerationResult(
                success=True,
                generated_files=[str(DEFAULT_OUTPUT)],
                errors=[],
                warnings=[],
                summary=f"Generated URL routes ({len(routes)} routes)",
            )
        except Exception as e:
            self.logger.error(f"URL route generation failed: {e}")
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=[str(e)],
                warnings=[],
                summary="URL route generation failed",
            )
    
    def validate_specification(self, spec_path: str) -> List[str]:
        """
        Validate OpenAPI specification.
        
        Args:
            spec_path: Path to OpenAPI specification file
            
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            self.spec_parser.load_spec(spec_path)
            entities = self.spec_parser.parse_entities()
            self._apply_entity_mapping_fallback()
            
            if not entities:
                return ["No entities found in OpenAPI specification"]
            
            errors = self.spec_parser.validate_configuration()
            return errors
            
        except Exception as e:
            return [f"Failed to validate specification: {e}"]
    
    def get_generation_info(self) -> Dict[str, Any]:
        """
        Get information about the generation system.
        
        Returns:
            Dictionary with generation system information
        """
        entities = self.spec_parser.get_all_entities() if self.spec_parser.entities else {}
        
        return {
            'entities_count': len(entities),
            'entities': list(entities.keys()),
            'templates_available': len(self.template_engine.list_templates()),
            'config': self.config,
            'generators': {
                'api_client': self.api_client_generator.get_generation_info(),
                'models': 'Available',
                'middleware': 'Available',
                'extensions': 'Available',
                'registry': 'Available',
            }
        }


