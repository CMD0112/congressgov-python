"""
Code Formatter for generated Python code.

This module provides utilities for:
- Formatting Python code with ruff
- Sorting imports with isort
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

_DEFAULT_RUFF_CONFIG = Path(__file__).resolve().parents[1] / "config" / "ruff_generated_client.toml"


@dataclass
class FormattingResult:
    """Result of code formatting operation."""

    success: bool
    original_content: str
    formatted_content: str
    changes_made: bool
    errors: List[str]
    warnings: List[str]


class CodeFormatter:
    """
    Formatter for Python code using isort and ruff.

    Features:
    - isort import sorting
    - ruff code formatting
    - Error handling and reporting
    """

    def __init__(
        self,
        use_ruff: bool = True,
        use_isort: bool = True,
        ruff_line_length: int = 120,
        ruff_config: Optional[Union[str, Path]] = None,
        isort_profile: str = "black",
        isort_multi_line: int = 3,
        isort_include_trailing_comma: bool = True,
        isort_force_grid_wrap: int = 0,
        isort_use_parentheses: bool = True,
        isort_ensure_newline_before_comments: bool = True,
    ):
        self.use_ruff = use_ruff
        self.use_isort = use_isort
        self.ruff_line_length = ruff_line_length
        self.ruff_config = Path(ruff_config) if ruff_config else _DEFAULT_RUFF_CONFIG
        self.isort_profile = isort_profile
        self.isort_multi_line = isort_multi_line
        self.isort_include_trailing_comma = isort_include_trailing_comma
        self.isort_force_grid_wrap = isort_force_grid_wrap
        self.isort_use_parentheses = isort_use_parentheses
        self.isort_ensure_newline_before_comments = isort_ensure_newline_before_comments

    def _check_tool_availability(self, tool_name: str) -> bool:
        try:
            result = subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def _run_ruff_format(
        self,
        content: str,
        file_path: Optional[Union[str, Path]] = None,
    ) -> FormattingResult:
        if not self.use_ruff:
            return FormattingResult(
                success=True,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=[],
                warnings=[],
            )

        if not self._check_tool_availability("ruff"):
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=["ruff is not available"],
                warnings=[],
            )

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            cmd = [
                "ruff",
                "format",
                temp_file_path,
                "--line-length",
                str(self.ruff_line_length),
            ]
            if self.ruff_config.is_file():
                cmd.extend(["--config", str(self.ruff_config)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            formatted_content = Path(temp_file_path).read_text(encoding="utf-8")
            Path(temp_file_path).unlink()

            if result.returncode == 0:
                changes_made = formatted_content != content
                return FormattingResult(
                    success=True,
                    original_content=content,
                    formatted_content=formatted_content,
                    changes_made=changes_made,
                    errors=[],
                    warnings=[],
                )
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=[result.stderr] if result.stderr else ["ruff formatting failed"],
                warnings=[],
            )

        except subprocess.TimeoutExpired:
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=["ruff formatting timed out"],
                warnings=[],
            )
        except Exception as e:
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=[f"ruff formatting error: {e!s}"],
                warnings=[],
            )

    def _run_isort(
        self,
        content: str,
        file_path: Optional[Union[str, Path]] = None,
    ) -> FormattingResult:
        if not self.use_isort:
            return FormattingResult(
                success=True,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=[],
                warnings=[],
            )

        if not self._check_tool_availability("isort"):
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=["isort is not available"],
                warnings=[],
            )

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            cmd = [
                "isort",
                "--profile",
                self.isort_profile,
                "--line-length",
                str(self.ruff_line_length),
                "--multi-line",
                str(self.isort_multi_line),
                "--quiet",
            ]

            if self.isort_include_trailing_comma:
                cmd.append("--trailing-comma")

            if self.isort_force_grid_wrap > 0:
                cmd.extend(["--force-grid-wrap", str(self.isort_force_grid_wrap)])

            if self.isort_use_parentheses:
                cmd.append("--use-parentheses")

            if self.isort_ensure_newline_before_comments:
                cmd.append("--ensure-newline-before-comments")

            cmd.append(temp_file_path)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            formatted_content = Path(temp_file_path).read_text(encoding="utf-8")
            Path(temp_file_path).unlink()

            if result.returncode == 0:
                changes_made = formatted_content != content
                return FormattingResult(
                    success=True,
                    original_content=content,
                    formatted_content=formatted_content,
                    changes_made=changes_made,
                    errors=[],
                    warnings=[],
                )
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=[result.stderr] if result.stderr else ["isort import sorting failed"],
                warnings=[],
            )

        except subprocess.TimeoutExpired:
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=["isort import sorting timed out"],
                warnings=[],
            )
        except Exception as e:
            return FormattingResult(
                success=False,
                original_content=content,
                formatted_content=content,
                changes_made=False,
                errors=[f"isort import sorting error: {e!s}"],
                warnings=[],
            )

    def format_content(
        self,
        content: str,
        file_path: Optional[Union[str, Path]] = None,
        apply_isort_first: bool = True,
    ) -> FormattingResult:
        original_content = content
        current_content = content
        all_errors: List[str] = []
        all_warnings: List[str] = []
        changes_made = False

        try:
            if apply_isort_first and self.use_isort:
                isort_result = self._run_isort(current_content, file_path)
                if isort_result.success:
                    current_content = isort_result.formatted_content
                    if isort_result.changes_made:
                        changes_made = True
                    logger.debug("Applied isort formatting")
                else:
                    all_errors.extend(isort_result.errors)
                    logger.warning("isort formatting failed: %s", isort_result.errors)

            if self.use_ruff:
                ruff_result = self._run_ruff_format(current_content, file_path)
                if ruff_result.success:
                    current_content = ruff_result.formatted_content
                    if ruff_result.changes_made:
                        changes_made = True
                    logger.debug("Applied ruff formatting")
                else:
                    all_errors.extend(ruff_result.errors)
                    logger.warning("ruff formatting failed: %s", ruff_result.errors)

            if not apply_isort_first and self.use_isort:
                isort_result = self._run_isort(current_content, file_path)
                if isort_result.success:
                    current_content = isort_result.formatted_content
                    if isort_result.changes_made:
                        changes_made = True
                    logger.debug("Applied isort formatting after ruff")
                else:
                    all_errors.extend(isort_result.errors)
                    logger.warning("isort formatting failed: %s", isort_result.errors)

            success = len(all_errors) == 0

            return FormattingResult(
                success=success,
                original_content=original_content,
                formatted_content=current_content,
                changes_made=changes_made,
                errors=all_errors,
                warnings=all_warnings,
            )

        except Exception as e:
            logger.error("Unexpected error during formatting: %s", e)
            return FormattingResult(
                success=False,
                original_content=original_content,
                formatted_content=original_content,
                changes_made=False,
                errors=[f"Unexpected formatting error: {e!s}"],
                warnings=[],
            )

    def format_file(
        self,
        file_path: Union[str, Path],
        in_place: bool = True,
    ) -> FormattingResult:
        file_path = Path(file_path)

        if not file_path.exists():
            return FormattingResult(
                success=False,
                original_content="",
                formatted_content="",
                changes_made=False,
                errors=[f"File not found: {file_path}"],
                warnings=[],
            )

        try:
            content = file_path.read_text(encoding="utf-8")
            result = self.format_content(content, file_path)

            if in_place and result.success and result.changes_made:
                file_path.write_text(result.formatted_content, encoding="utf-8")
                logger.info("Formatted file: %s", file_path)

            return result

        except Exception as e:
            logger.error("Error formatting file %s: %s", file_path, e)
            return FormattingResult(
                success=False,
                original_content="",
                formatted_content="",
                changes_made=False,
                errors=[f"File formatting error: {e!s}"],
                warnings=[],
            )

    def get_formatting_config(self) -> Dict[str, Any]:
        return {
            "use_ruff": self.use_ruff,
            "use_isort": self.use_isort,
            "ruff_line_length": self.ruff_line_length,
            "ruff_config": str(self.ruff_config),
            "isort_profile": self.isort_profile,
            "isort_multi_line": self.isort_multi_line,
            "isort_include_trailing_comma": self.isort_include_trailing_comma,
            "isort_force_grid_wrap": self.isort_force_grid_wrap,
            "isort_use_parentheses": self.isort_use_parentheses,
            "isort_ensure_newline_before_comments": self.isort_ensure_newline_before_comments,
        }
