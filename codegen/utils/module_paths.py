"""Normalize legacy dotted paths from OpenAPI annotations to src layout."""

from __future__ import annotations


def normalize_module_path(path: str) -> str:
    path = path.strip()
    if path.startswith("congressgov."):
        return path
    if path.startswith("models."):
        return f"congressgov.{path}"
    return path


def normalize_service_path(path: str) -> str:
    path = path.strip()
    if path.startswith("congressgov."):
        return path
    if path.startswith("middleware."):
        return path.replace("middleware.", "congressgov.services.", 1)
    return path


def normalize_extension_path(path: str) -> str:
    path = path.strip()
    if path.startswith("congressgov."):
        return path
    if path.startswith("middleware.extensions."):
        return path.replace("middleware.extensions.", "congressgov.services.extensions.", 1)
    if path.startswith("middleware."):
        return path.replace("middleware.", "congressgov.services.", 1)
    return path
