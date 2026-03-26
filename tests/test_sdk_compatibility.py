"""Tests that catch intersect-sdk compatibility issues early.

These tests validate that:
1. The capability name matches SDK 0.9+ regex (alphanumeric + underscores only).
2. All @intersect_message parameter/return type annotations are resolvable at
   runtime (i.e. not lazily stringified by ``from __future__ import annotations``).
"""

import ast
import re
from pathlib import Path

from intersect_sdk import (
    HierarchyConfig,
    get_schema_from_capability_implementations,
)

from chess_instrument_control_service.service import ChessInstrumentControlCapability

SRC_DIR = Path(__file__).resolve().parent.parent / "src" / "chess_instrument_control_service"

HIERARCHY = HierarchyConfig(
    organization="test-org",
    facility="test-facility",
    system="test-system",
    subsystem="test-sub",
    service="test-svc",
)


# ------------------------------------------------------------------
# 1. Capability name must satisfy SDK 0.9+ regex
# ------------------------------------------------------------------
class TestCapabilityNameValid:
    """SDK 0.9 requires names matching ^[a-zA-Z0-9]\\w*$ (no hyphens)."""

    SDK_NAME_REGEX = re.compile(r"^[a-zA-Z0-9]\w*$")

    def test_capability_name_matches_sdk_regex(self):
        name = ChessInstrumentControlCapability.intersect_sdk_capability_name
        assert isinstance(name, str) and name, (
            "intersect_sdk_capability_name must be a non-empty string"
        )
        assert self.SDK_NAME_REGEX.fullmatch(name), (
            f"intersect_sdk_capability_name '{name}' does not satisfy SDK regex "
            f"{self.SDK_NAME_REGEX.pattern!r} — hyphens are not allowed, use underscores"
        )


# ------------------------------------------------------------------
# 2. Schema generation must succeed (catches TypeAdapter / annotation issues)
# ------------------------------------------------------------------
class TestSchemaGeneration:
    """``get_schema_from_capability_implementations`` exercises the same
    TypeAdapter introspection the SDK performs at service start-up.
    If ``from __future__ import annotations`` is present, Pydantic will
    receive *string* annotations it cannot resolve and raise an error.
    """

    def test_schema_generation_succeeds(self):
        schema = get_schema_from_capability_implementations(
            [ChessInstrumentControlCapability], HIERARCHY
        )
        assert "capabilities" in schema

    def test_schema_contains_capability(self):
        schema = get_schema_from_capability_implementations(
            [ChessInstrumentControlCapability], HIERARCHY
        )
        cap_name = ChessInstrumentControlCapability.intersect_sdk_capability_name
        assert cap_name in schema["capabilities"], (
            f"Capability '{cap_name}' missing from generated schema"
        )


# ------------------------------------------------------------------
# 3. Guard against ``from __future__ import annotations`` in source files
#    that define Pydantic models or SDK capability classes
# ------------------------------------------------------------------
class TestNoFutureAnnotations:
    """``from __future__ import annotations`` (PEP 563) turns all annotations
    into lazy strings, which breaks both Pydantic's ``TypeAdapter`` and the
    intersect-sdk schema introspection at service start-up.

    This test statically checks every Python file under the package source
    so the issue is caught *before* the service attempts to boot.
    """

    @staticmethod
    def _has_future_annotations(filepath: Path) -> bool:
        """Return True if the file contains ``from __future__ import annotations``."""
        tree = ast.parse(filepath.read_text())
        return any(
            isinstance(node, ast.ImportFrom)
            and node.module == "__future__"
            and any(alias.name == "annotations" for alias in node.names)
            for node in ast.iter_child_nodes(tree)
        )

    @staticmethod
    def _uses_pydantic_or_sdk(filepath: Path) -> bool:
        """Return True if the file imports from pydantic or intersect_sdk."""
        text = filepath.read_text()
        return "pydantic" in text or "intersect_sdk" in text

    def test_no_future_annotations_in_model_or_sdk_files(self):
        """Files that use Pydantic or intersect_sdk must NOT use PEP 563."""
        violations = []
        for py_file in sorted(SRC_DIR.rglob("*.py")):
            if self._uses_pydantic_or_sdk(py_file) and self._has_future_annotations(py_file):
                violations.append(py_file.relative_to(SRC_DIR.parent.parent))

        assert not violations, (
            "These files use 'from __future__ import annotations' alongside "
            "Pydantic/intersect_sdk, which breaks runtime type resolution:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )
