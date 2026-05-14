"""Layout subagent: wraps TieredLayout for use inside the orchestrator."""

from __future__ import annotations

from aether.layout.tiered import LayoutPlan, TieredLayout
from aether.schemas.architecture import Architecture


class LayoutSubagent:
    def __init__(self, layout: TieredLayout | None = None) -> None:
        self.layout = layout or TieredLayout()

    def plan(self, arch: Architecture) -> LayoutPlan:
        return self.layout.plan(arch)
