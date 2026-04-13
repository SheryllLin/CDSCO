from __future__ import annotations

from typing import Any


class OptionalDependencyMixin:
    """Allows services to degrade gracefully when optional ML packages are absent."""

    def dependency_status(self) -> dict[str, Any]:
        return {}
