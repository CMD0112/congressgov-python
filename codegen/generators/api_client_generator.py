"""
API Client Generator using openapi-python-client.

This module generates the API client by wrapping openapi-python-client
and provides integration with the rest of the code generation system.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_generator import BaseGenerator, GenerationResult

logger = logging.getLogger(__name__)


class ApiClientGenerator(BaseGenerator):
    """
    Generator for API client using openapi-python-client.
    
    This generator:
    - Runs openapi-python-client to generate the base API client
    - Handles configuration and output directory setup
    - Provides integration with the rest of the code generation system
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        spec_parser: Any,
        file_manager: Optional[Any] = None,
        template_engine: Optional[Any] = None,
        code_formatter: Optional[Any] = None
    ):
        """
        Initialize ApiClientGenerator.
        
        Args:
            config: Generator configuration
            spec_parser: Parsed OpenAPI specification
            file_manager: File manager instance
            template_engine: Template engine instance
            code_formatter: Code formatter instance
        """
        super().__init__(config, spec_parser, file_manager, template_engine, code_formatter)
        
        # API client specific configuration
        self.api_client_config = config.get('api_client', {})
        self.output_config = config.get('output', {})
    
    def generate(self) -> GenerationResult:
        """
        Generate API client using openapi-python-client.
        
        Returns:
            GenerationResult with success status and details
        """
        self.logger.info("Starting API client generation...")
        
        try:
            # Validate prerequisites
            errors = self.validate_generation_prerequisites()
            if errors:
                return self.create_generation_result(
                    success=False,
                    generated_files=[],
                    errors=errors,
                    summary="API client generation failed validation"
                )
            
            output_dir = self.get_output_directory('api_client')
            staging_dir = Path(tempfile.mkdtemp(prefix="congressgov_client_"))
            try:
                cmd = self._prepare_openapi_command(staging_dir)
                success, _output, errors = self._run_openapi_client(cmd)

                if not success:
                    return self.create_generation_result(
                        success=False,
                        generated_files=[],
                        errors=errors,
                        summary=(
                            "API client generation failed; existing "
                            f"{output_dir.as_posix()}/ was not modified"
                        ),
                    )

                generated_files = self._promote_staging_client(staging_dir, output_dir)
            finally:
                if staging_dir.exists():
                    shutil.rmtree(staging_dir, ignore_errors=True)
            
            self.logger.info(f"API client generation completed. Generated {len(generated_files)} files")
            
            return self.create_generation_result(
                success=True,
                generated_files=generated_files,
                warnings=[] if success else ["API client generation completed with warnings"],
                summary=f"Successfully generated API client with {len(generated_files)} files"
            )
            
        except Exception as e:
            self.logger.error(f"API client generation failed: {e}")
            return self.create_generation_result(
                success=False,
                generated_files=[],
                errors=[str(e)],
                summary="API client generation failed with exception"
            )
    
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys.
        
        Returns:
            List of required configuration key names
        """
        return ['output', 'api_client']
    
    def _prepare_openapi_command(self, output_dir: Path) -> List[str]:
        """
        Prepare openapi-python-client command.
        
        Args:
            output_dir: Output directory for generated client
            
        Returns:
            List of command arguments
        """
        # Base command
        cmd = ['openapi-python-client', 'generate']
        
        # Add OpenAPI spec path
        spec_path = self.config.get('spec_path')
        if spec_path:
            cmd.extend(['--path', str(spec_path)])
        
        meta = self.api_client_config.get('meta', 'none')
        cmd.extend(['--output-path', str(output_dir)])
        cmd.extend(['--meta', meta])
        cmd.append('--overwrite')

        config_path = self.api_client_config.get('config_path')
        if config_path:
            cmd.extend(['--config', str(config_path)])
        else:
            default_config = Path(__file__).resolve().parents[1] / 'config' / 'openapi_client_config.yaml'
            if default_config.exists():
                cmd.extend(['--config', str(default_config)])

        skip_option_keys = {
            'meta', 'url', 'package_name', 'package_version', 'package_description',
        }
        options = self.api_client_config.get('options', {})
        for key, value in options.items():
            if value is not None and key not in skip_option_keys:
                flag = key.replace('_', '-')
                cmd.extend([f'--{flag}', str(value)])
        
        self.logger.debug(f"Prepared command: {' '.join(cmd)}")
        return cmd
    
    def _run_openapi_client(self, cmd: List[str]) -> tuple[bool, str, List[str]]:
        """
        Run openapi-python-client command.
        
        Args:
            cmd: Command to run
            
        Returns:
            Tuple of (success, output, errors)
        """
        try:
            self.logger.info(f"Running openapi-python-client: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info("openapi-python-client completed successfully")
                return True, result.stdout, []
            else:
                errors = []
                if result.stderr:
                    errors.append(f"openapi-python-client stderr: {result.stderr}")
                if result.stdout:
                    errors.append(f"openapi-python-client stdout: {result.stdout}")
                
                self.logger.error(f"openapi-python-client failed with return code {result.returncode}")
                return False, result.stdout, errors
                
        except subprocess.TimeoutExpired:
            error_msg = "openapi-python-client timed out after 5 minutes"
            self.logger.error(error_msg)
            return False, "", [error_msg]
            
        except FileNotFoundError:
            error_msg = "openapi-python-client not found. Please install it with: pip install openapi-python-client"
            self.logger.error(error_msg)
            return False, "", [error_msg]
            
        except Exception as e:
            error_msg = f"Error running openapi-python-client: {e}"
            self.logger.error(error_msg)
            return False, "", [error_msg]
    
    def _find_generated_files(self, output_dir: Path) -> List[Path]:
        """
        Find generated files in the output directory.
        
        Args:
            output_dir: Output directory to search
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        if not output_dir.exists():
            self.logger.warning(f"Output directory does not exist: {output_dir}")
            return generated_files
        
        # Find Python files recursively
        for py_file in output_dir.rglob('*.py'):
            if py_file.is_file() and not py_file.name.startswith('__'):
                generated_files.append(py_file)
        
        # Sort files for consistent output
        generated_files.sort()
        
        self.logger.debug(f"Found {len(generated_files)} generated Python files")
        return generated_files

    def _promote_staging_client(
        self, staging_dir: Path, output_dir: Path
    ) -> List[Path]:
        """Replace output client tree only after a successful staging generation."""
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=True)
        shutil.copytree(staging_dir, output_dir, ignore=shutil.ignore_patterns("__pycache__"))
        self.logger.info(
            "Promoted staged API client from %s to %s",
            staging_dir,
            output_dir,
        )
        return self._find_generated_files(output_dir)
    
    def validate_openapi_client_availability(self) -> bool:
        """
        Check if openapi-python-client is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            result = subprocess.run(
                ['openapi-python-client', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_generation_info(self) -> Dict[str, Any]:
        """
        Get information about the API client generation.
        
        Returns:
            Dictionary with generation information
        """
        return {
            'generator': 'openapi-python-client',
            'version': self.api_client_config.get('version', '>=0.25.3'),
            'output_directory': self.output_config.get('api_client'),
            'package_name': self.api_client_config.get('package_name'),
            'available': self.validate_openapi_client_availability()
        }
    
    def validate_generation_prerequisites(self) -> List[str]:
        """
        Validate prerequisites for API client generation.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        config_errors = self.validate_configuration()
        errors.extend(config_errors)
        
        # Check if openapi-python-client is available
        if not self.validate_openapi_client_availability():
            errors.append("openapi-python-client is not available. Install with: pip install openapi-python-client")
        
        # Check if spec file exists
        spec_path = self.config.get('spec_path')
        if spec_path and not Path(spec_path).exists():
            errors.append(f"OpenAPI specification file not found: {spec_path}")
        
        return errors


