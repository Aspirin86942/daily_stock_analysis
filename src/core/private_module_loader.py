# -*- coding: utf-8 -*-
"""Utilities for loading optional private modules at runtime."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Optional, Sequence

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_MODULE_CACHE: dict[str, ModuleType] = {}


def get_private_modules_dir() -> Path:
    """Resolve the private modules directory from env or default location."""
    configured_dir = os.getenv("PRIVATE_MODULES_DIR", "").strip()
    if not configured_dir:
        return _PROJECT_ROOT / "private" / "modules"

    resolved_dir = Path(configured_dir).expanduser()
    if resolved_dir.is_absolute():
        return resolved_dir
    return (_PROJECT_ROOT / resolved_dir).resolve()


def build_private_file_candidates(module_stem: str, legacy_relative_paths: Sequence[str] = ()) -> list[Path]:
    """Build unique candidate file paths for one optional private module."""
    candidates = [get_private_modules_dir() / f"{module_stem}.py"]
    candidates.extend((_PROJECT_ROOT / relative_path).resolve() for relative_path in legacy_relative_paths)

    unique_candidates: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        marker = str(path)
        if marker in seen:
            continue
        seen.add(marker)
        unique_candidates.append(path)
    return unique_candidates


def load_optional_class(
    class_name: str,
    module_candidates: Sequence[str],
    file_candidates: Sequence[Path] = (),
) -> Optional[type[Any]]:
    """Load an optional class from import candidates or file candidates."""
    for module_name in module_candidates:
        module = _load_module_from_import(module_name)
        loaded_class = _extract_class(module, class_name)
        if loaded_class is not None:
            return loaded_class

    for file_path in file_candidates:
        module = _load_module_from_file(file_path)
        loaded_class = _extract_class(module, class_name)
        if loaded_class is not None:
            return loaded_class

    return None


def _extract_class(module: Optional[ModuleType], class_name: str) -> Optional[type[Any]]:
    if module is None or not hasattr(module, class_name):
        return None
    candidate = getattr(module, class_name)
    return candidate if isinstance(candidate, type) else None


def _load_module_from_import(module_name: str) -> Optional[ModuleType]:
    if module_name in _MODULE_CACHE:
        return _MODULE_CACHE[module_name]

    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None

    _MODULE_CACHE[module_name] = module
    return module


def _load_module_from_file(file_path: Path) -> Optional[ModuleType]:
    if not file_path.exists():
        return None

    resolved_path = file_path.resolve()
    module_key = _build_file_module_cache_key(resolved_path)
    if module_key in _MODULE_CACHE:
        return _MODULE_CACHE[module_key]

    spec = importlib.util.spec_from_file_location(module_key, resolved_path)
    if spec is None or spec.loader is None:
        return None

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        return None

    _MODULE_CACHE[module_key] = module
    return module


def _build_file_module_cache_key(file_path: Path) -> str:
    digest = hashlib.md5(str(file_path).encode("utf-8")).hexdigest()
    return f"_private_dynamic_{file_path.stem}_{digest}"
