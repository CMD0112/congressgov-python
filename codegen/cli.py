"""
Command-line interface for the code generation system.

This module provides CLI commands for generating different components
of the congressgov project from OpenAPI specifications.
"""

from __future__ import annotations

import logging
import sys
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

import click


def _status(prefix: str, message: str) -> None:
    """Print CLI status without Unicode symbols (Windows cp1252 safe)."""
    click.echo(f"{prefix} {message}", file=sys.stdout)

from .main import CodeGenerationSystem
from .processors.spec_parser import SpecParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', help='Path to configuration file')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """congressgov code generation system."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config_path = config or 'codegen/config/generator_config.yaml'
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config_path


@cli.command()
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
@click.option('--config', '-c', help='Path to generator configuration')
@click.pass_context
def generate_all(ctx: click.Context, spec: str, config: Optional[str]) -> None:
    """Generate entire project from OpenAPI specification."""
    try:
        # Load configuration
        config_path = _resolve_config_path(ctx, config)
        config_data = _load_config(config_path)
        
        # Create generation system
        system = CodeGenerationSystem(config_data)
        
        # Run full generation
        result = system.generate_all(spec_path=spec)
        
        if result.success:
            _status("OK:", "Generation completed successfully!")
            click.echo(f"Generated {len(result.generated_files)} files")
            for file_path in result.generated_files:
                click.echo(f"  - {file_path}")
        else:
            _status("ERROR:", "Generation failed!")
            for error in result.errors:
                click.echo(f"  - {error}")
            raise click.Abort()
            
    except Exception as e:
        _status("ERROR:", f"Generation failed: {e}")
        raise click.Abort()


@cli.command()
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
@click.option('--config', '-c', help='Path to generator configuration')
@click.pass_context
def generate_client(ctx: click.Context, spec: str, config: Optional[str]) -> None:
    """Generate only API client."""
    try:
        # Load configuration
        config_path = _resolve_config_path(ctx, config)
        config_data = _load_config(config_path)
        
        # Create generation system
        system = CodeGenerationSystem(config_data)
        
        # Run API client generation
        result = system.generate_api_client(spec_path=spec)
        
        if result.success:
            _status("OK:", "API client generation completed successfully!")
            click.echo(f"Generated {len(result.generated_files)} files")
            for file_path in result.generated_files:
                click.echo(f"  - {file_path}")
        else:
            _status("ERROR:", "API client generation failed!")
            for error in result.errors:
                click.echo(f"  - {error}")
            raise click.Abort()
            
    except Exception as e:
        _status("ERROR:", f"API client generation failed: {e}")
        raise click.Abort()


@cli.command()
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
@click.option('--config', '-c', help='Path to generator configuration')
@click.pass_context
def generate_models(ctx: click.Context, spec: str, config: Optional[str]) -> None:
    """Generate only models."""
    try:
        # Load configuration
        config_path = _resolve_config_path(ctx, config)
        config_data = _load_config(config_path)
        
        # Create generation system
        system = CodeGenerationSystem(config_data)
        system.prepare_spec(spec)
        
        # Run model generation
        result = system.generate_models(spec_path=spec)
        
        if result.success:
            _status("OK:", "Model generation completed successfully!")
            click.echo(f"Generated {len(result.generated_files)} files")
            for file_path in result.generated_files:
                click.echo(f"  - {file_path}")
        else:
            _status("ERROR:", "Model generation failed!")
            for error in result.errors:
                click.echo(f"  - {error}")
            raise click.Abort()
            
    except Exception as e:
        _status("ERROR:", f"Model generation failed: {e}")
        raise click.Abort()


@cli.command("generate-registry")
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
@click.option('--config', '-c', help='Path to generator configuration')
@click.pass_context
def generate_registry(ctx: click.Context, spec: str, config: Optional[str]) -> None:
    """Generate model registry artifact."""
    _run_generation_step(ctx, config, spec, "registry", "Registry")


@cli.command("generate-extensions")
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
@click.option('--config', '-c', help='Path to generator configuration')
@click.pass_context
def generate_extensions(ctx: click.Context, spec: str, config: Optional[str]) -> None:
    """Generate middleware extension modules."""
    _run_generation_step(ctx, config, spec, "extensions", "Extension")


@cli.command("generate-url-routes")
@click.option(
    "--aliases",
    default="codegen/config/legacy_client_aliases.yaml",
    help="Path to legacy client aliases YAML",
)
@click.option(
    "--output",
    default="src/congressgov/services/core/url_routes_generated.py",
    help="Output path for generated route table",
)
def generate_url_routes(aliases: str, output: str) -> None:
    """Generate URL route table for fetch_from_url."""
    from codegen.scripts.generate_url_routes import main as run_main
    import sys

    sys.argv = ["generate_url_routes", "--aliases", aliases, "--output", output]
    raise SystemExit(run_main())


def _run_generation_step(
    ctx: click.Context,
    config: Optional[str],
    spec: str,
    step: str,
    label: str,
) -> None:
    try:
        config_path = _resolve_config_path(ctx, config)
        config_data = _load_config(config_path)
        system = CodeGenerationSystem(config_data)
        system.prepare_spec(spec)
        runners = {
            "registry": system.generate_registry,
            "extensions": system.generate_extensions,
        }
        result = runners[step](spec_path=spec)
        if result.success:
            _status("OK:", f"{label} generation completed successfully!")
            click.echo(f"Generated {len(result.generated_files)} files")
            for file_path in result.generated_files:
                click.echo(f"  - {file_path}")
        else:
            _status("ERROR:", f"{label} generation failed!")
            for error in result.errors:
                click.echo(f"  - {error}")
            raise click.Abort()
    except click.Abort:
        raise
    except Exception as e:
        _status("ERROR:", f"{label} generation failed: {e}")
        raise click.Abort()


@cli.command()
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
@click.option('--config', '-c', help='Path to generator configuration')
@click.pass_context
def generate_middleware(ctx: click.Context, spec: str, config: Optional[str]) -> None:
    """Generate middleware service classes."""
    try:
        # Load configuration
        config_path = _resolve_config_path(ctx, config)
        config_data = _load_config(config_path)
        
        # Create generation system
        system = CodeGenerationSystem(config_data)
        system.prepare_spec(spec)
        
        # Run middleware generation
        result = system.generate_middleware(spec_path=spec)
        
        if result.success:
            _status("OK:", "Middleware generation completed successfully!")
            click.echo(f"Generated {len(result.generated_files)} files")
            for file_path in result.generated_files:
                click.echo(f"  - {file_path}")
        else:
            _status("ERROR:", "Middleware generation failed!")
            for error in result.errors:
                click.echo(f"  - {error}")
            raise click.Abort()
            
    except Exception as e:
        _status("ERROR:", f"Middleware generation failed: {e}")
        raise click.Abort()


@cli.command()
@click.option('--spec', default='codegen/config/openapi_spec.yaml', help='Path to OpenAPI specification')
def validate_spec(spec: str) -> None:
    """Validate OpenAPI specification."""
    try:
        # Load and parse spec
        spec_path = Path(spec)
        if not spec_path.exists():
            _status("ERROR:", f"Specification file not found: {spec}")
            raise click.Abort()
        
        parser = SpecParser()
        parser.load_spec(spec_path)
        entities = parser.parse_entities()
        
        # Validate configuration
        errors = parser.validate_configuration()
        
        if errors:
            _status("ERROR:", "Specification validation failed!")
            for error in errors:
                click.echo(f"  - {error}")
            raise click.Abort()
        else:
            _status("OK:", "Specification validation passed!")
            click.echo(f"Found {len(entities)} entities:")
            for entity_name in entities.keys():
                click.echo(f"  - {entity_name}")
                
    except Exception as e:
        _status("ERROR:", f"Specification validation failed: {e}")
        raise click.Abort()


@cli.command()
def list_templates() -> None:
    """List available templates."""
    try:
        from .utils.template_engine import TemplateEngine
        
        # Create template engine
        template_dirs = [Path(__file__).parent / "templates"]
        engine = TemplateEngine(template_dirs)
        
        # List templates
        templates = engine.list_templates()
        
        click.echo("Available templates:")
        for template in templates:
            click.echo(f"  - {template}")
            
    except Exception as e:
        _status("ERROR:", f"Failed to list templates: {e}")
        raise click.Abort()


def _resolve_config_path(ctx: click.Context, config: Optional[str]) -> str:
    """Resolve config path when invoked as a Poetry script (no Click group context)."""
    if config:
        return config
    if ctx.obj and ctx.obj.get("config_path"):
        return ctx.obj["config_path"]
    return "codegen/config/generator_config.yaml"


def _load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    return config_data


if __name__ == '__main__':
    cli()


