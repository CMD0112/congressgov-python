"""
File Manager for safe file operations with backup and incremental updates.

This module provides utilities for:
- Safe file writing with automatic backups
- Incremental file updates preserving custom modifications
- File existence and permission checking
- Directory creation and management
"""

from __future__ import annotations

import os
import shutil
import logging
from pathlib import Path
from typing import Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manager for safe file operations with backup and incremental update support.
    
    Features:
    - Automatic backup creation before overwriting files
    - Incremental updates preserving custom modifications
    - Safe directory creation
    - File permission and existence checking
    """
    
    def __init__(
        self,
        backup_suffix: str = ".backup",
        custom_marker: str = "# CUSTOM:",
        generated_marker: str = "# GENERATED:",
        create_backups: bool = True,
        protected_paths: Optional[list[str]] = None,
    ):
        """
        Initialize FileManager.
        
        Args:
            backup_suffix: Suffix for backup files
            custom_marker: Marker for custom sections to preserve
            generated_marker: Marker for generated sections
            create_backups: Whether to create backups before overwriting
            protected_paths: Repo-relative paths or directory prefixes to skip on write
        """
        self.backup_suffix = backup_suffix
        self.custom_marker = custom_marker
        self.generated_marker = generated_marker
        self.create_backups = create_backups
        self.protected_paths = [p.replace("\\", "/").rstrip("/") for p in (protected_paths or [])]

    def is_protected(self, path: Union[str, Path]) -> bool:
        """Return True if path is under a protected prefix or exact protected file."""
        normalized = Path(path).as_posix().lstrip("./")
        for protected in self.protected_paths:
            if normalized == protected or normalized.startswith(f"{protected}/"):
                return True
        return False
    
    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, creating it if necessary.
        
        Args:
            path: Directory path
            
        Returns:
            Path object for the directory
            
        Raises:
            OSError: If directory cannot be created
        """
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")
        return dir_path
    
    def file_exists(self, path: Union[str, Path]) -> bool:
        """
        Check if file exists and is readable.
        
        Args:
            path: File path
            
        Returns:
            True if file exists and is readable
        """
        file_path = Path(path)
        return file_path.exists() and file_path.is_file() and os.access(file_path, os.R_OK)
    
    def create_backup(self, path: Union[str, Path]) -> Optional[Path]:
        """
        Create backup of existing file.
        
        Args:
            path: File path to backup
            
        Returns:
            Path to backup file, or None if no backup was created
        """
        file_path = Path(path)
        
        if not self.create_backups or not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}{self.backup_suffix}")
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            raise
    
    def write_file(
        self,
        path: Union[str, Path],
        content: str,
        create_backup: Optional[bool] = None,
        ensure_dir: bool = True
    ) -> Path:
        """
        Write content to file with optional backup.
        
        Args:
            path: File path
            content: Content to write
            create_backup: Whether to create backup (overrides instance setting)
            ensure_dir: Whether to ensure directory exists
            
        Returns:
            Path to written file
        """
        file_path = Path(path)
        
        if self.is_protected(file_path):
            logger.info(f"Skipped protected path: {file_path}")
            return file_path
        
        # Ensure directory exists if requested
        if ensure_dir:
            self.ensure_directory(file_path.parent)
        
        # Create backup if requested and file exists
        should_backup = create_backup if create_backup is not None else self.create_backups
        if should_backup and file_path.exists():
            self.create_backup(file_path)
        
        # Write content
        try:
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"Wrote file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise
    
    def read_file(self, path: Union[str, Path]) -> str:
        """
        Read file content.
        
        Args:
            path: File path
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise IOError(f"Path is not a file: {file_path}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            logger.debug(f"Read file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    def merge_incremental(
        self,
        existing_content: str,
        generated_content: str,
        custom_marker: Optional[str] = None,
        generated_marker: Optional[str] = None
    ) -> str:
        """
        Merge existing content with generated content, preserving custom sections.
        
        This method:
        1. Identifies custom sections (marked with custom_marker)
        2. Preserves custom sections in the final content
        3. Replaces generated sections with new generated content
        4. Maintains file structure and comments
        
        Args:
            existing_content: Current file content
            generated_content: New generated content
            custom_marker: Marker for custom sections (uses instance default if None)
            generated_marker: Marker for generated sections (uses instance default if None)
            
        Returns:
            Merged content
        """
        custom_marker = custom_marker or self.custom_marker
        generated_marker = generated_marker or self.generated_marker
        
        existing_lines = existing_content.splitlines()
        generated_lines = generated_content.splitlines()
        
        result_lines = []
        i = 0
        
        while i < len(existing_lines):
            line = existing_lines[i]
            
            # Check if this is a custom section marker
            if custom_marker in line:
                # Preserve the entire custom section
                result_lines.append(line)
                i += 1
                
                # Add all lines until we hit the next section marker or end of file
                while i < len(existing_lines):
                    next_line = existing_lines[i]
                    if (generated_marker in next_line or 
                        (custom_marker in next_line and next_line.strip().startswith(custom_marker))):
                        break
                    result_lines.append(next_line)
                    i += 1
                
                # Don't increment i here, let the outer loop handle it
                continue
            
            # Check if this is a generated section marker
            elif generated_marker in line:
                # Skip this line and all subsequent lines until next marker
                i += 1
                while i < len(existing_lines):
                    next_line = existing_lines[i]
                    if (custom_marker in next_line or 
                        (generated_marker in next_line and next_line.strip().startswith(generated_marker))):
                        break
                    i += 1
                # Don't increment i here, let the outer loop handle it
                continue
            
            # Regular line - preserve it
            else:
                result_lines.append(line)
                i += 1
        
        # Add the new generated content
        result_lines.extend(generated_lines)
        
        return '\n'.join(result_lines)
    
    def write_incremental(
        self,
        path: Union[str, Path],
        generated_content: str,
        create_backup: Optional[bool] = None,
        custom_marker: Optional[str] = None,
        generated_marker: Optional[str] = None
    ) -> Path:
        """
        Write content to file with incremental update support.
        
        If file exists, merges new content with existing content, preserving
        custom sections. If file doesn't exist, creates it with new content.
        
        Args:
            path: File path
            generated_content: New generated content
            create_backup: Whether to create backup (overrides instance setting)
            custom_marker: Marker for custom sections
            generated_marker: Marker for generated sections
            
        Returns:
            Path to written file
        """
        file_path = Path(path)
        
        # If file doesn't exist, just write the content
        if not file_path.exists():
            return self.write_file(file_path, generated_content, create_backup)
        
        # File exists - read existing content and merge
        try:
            existing_content = self.read_file(file_path)
            merged_content = self.merge_incremental(
                existing_content,
                generated_content,
                custom_marker,
                generated_marker
            )
            return self.write_file(file_path, merged_content, create_backup)
        except Exception as e:
            logger.error(f"Failed to write incremental update to {file_path}: {e}")
            raise
    
    def remove_file(self, path: Union[str, Path], create_backup: bool = True) -> bool:
        """
        Remove file with optional backup.
        
        Args:
            path: File path
            create_backup: Whether to create backup before removal
            
        Returns:
            True if file was removed, False if it didn't exist
        """
        file_path = Path(path)
        
        if not file_path.exists():
            return False
        
        if create_backup:
            self.create_backup(file_path)
        
        try:
            file_path.unlink()
            logger.info(f"Removed file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
            raise
    
    def copy_file(
        self,
        src: Union[str, Path],
        dst: Union[str, Path],
        create_backup: bool = True
    ) -> Path:
        """
        Copy file from source to destination.
        
        Args:
            src: Source file path
            dst: Destination file path
            create_backup: Whether to create backup of destination if it exists
            
        Returns:
            Path to destination file
        """
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
        
        # Ensure destination directory exists
        self.ensure_directory(dst_path.parent)
        
        # Create backup of destination if it exists
        if dst_path.exists() and create_backup:
            self.create_backup(dst_path)
        
        try:
            shutil.copy2(src_path, dst_path)
            logger.info(f"Copied file: {src_path} -> {dst_path}")
            return dst_path
        except Exception as e:
            logger.error(f"Failed to copy file {src_path} to {dst_path}: {e}")
            raise
    
    def get_file_stats(self, path: Union[str, Path]) -> dict[str, Any]:
        """
        Get file statistics.
        
        Args:
            path: File path
            
        Returns:
            Dictionary with file statistics
        """
        file_path = Path(path)
        
        if not file_path.exists():
            return {"exists": False}
        
        stat = file_path.stat()
        return {
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "is_readable": os.access(file_path, os.R_OK),
            "is_writable": os.access(file_path, os.W_OK),
        }


