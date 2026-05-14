"""Tiered layout planner.

Implements the PDF Layout Rules:
  * Tiered organization: Web (top), App, Data
  * Horizontal spacing 40-60px within a tier
  * Vertical spacing 80-120px between tiers
  * A4 landscape canvas constraint: 1169px x 827px
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aether.schemas.architecture import Architecture, Component, Tier


# A4 landscape in pixels at 96 DPI (the PDF's stated default).
CANVAS_W = 1169
CANVAS_H = 827

NODE_W = 120
NODE_H = 80

H_GAP = 50      # horizontal spacing within a tier (PDF range: 40-60px)
V_GAP = 100     # vertical spacing between tiers (PDF range: 80-120px)
MARGIN_X = 40
MARGIN_Y = 40

# Top-to-bottom order of tiers. Observability is rendered as a side band
# rather than another row so that primary request flow stays vertical.
TIER_ORDER: list[Tier] = [
    Tier.CLIENT,
    Tier.EDGE,
    Tier.WEB,
    Tier.APP,
    Tier.DATA,
]


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    w: int
    h: int


@dataclass
class LayoutPlan:
    boxes: dict[str, Box] = field(default_factory=dict)
    canvas_w: int = CANVAS_W
    canvas_h: int = CANVAS_H

    def get(self, component_id: str) -> Box:
        return self.boxes[component_id]


class TieredLayout:
    """Place components into rows by tier, centered horizontally."""

    def __init__(
        self,
        node_w: int = NODE_W,
        node_h: int = NODE_H,
        h_gap: int = H_GAP,
        v_gap: int = V_GAP,
    ) -> None:
        if not 40 <= h_gap <= 60:
            raise ValueError("h_gap must be 40-60px per PDF Layout Rule")
        if not 80 <= v_gap <= 120:
            raise ValueError("v_gap must be 80-120px per PDF Layout Rule")
        self.node_w = node_w
        self.node_h = node_h
        self.h_gap = h_gap
        self.v_gap = v_gap

    def plan(self, arch: Architecture) -> LayoutPlan:
        # Bucket components by resolved tier.
        buckets: dict[Tier, list[Component]] = {t: [] for t in TIER_ORDER}
        observability: list[Component] = []
        for c in arch.components:
            t = c.resolved_tier
            if t == Tier.OBSERVABILITY:
                observability.append(c)
            else:
                buckets.setdefault(t, []).append(c)

        plan = LayoutPlan()
        # Compute canvas height needed for primary tiers.
        active_tiers = [t for t in TIER_ORDER if buckets.get(t)]
        rows = len(active_tiers)
        needed_h = MARGIN_Y * 2 + rows * self.node_h + max(0, rows - 1) * self.v_gap
        plan.canvas_h = max(CANVAS_H, needed_h)

        # Width needed by the widest tier.
        widest = max(
            (len(buckets[t]) for t in active_tiers),
            default=1,
        )
        needed_w = (
            MARGIN_X * 2
            + widest * self.node_w
            + max(0, widest - 1) * self.h_gap
            + (self.node_w + self.h_gap if observability else 0)
        )
        plan.canvas_w = max(CANVAS_W, needed_w)

        y = MARGIN_Y
        for tier in active_tiers:
            row = buckets[tier]
            row_width = (
                len(row) * self.node_w + max(0, len(row) - 1) * self.h_gap
            )
            # Center the row within the primary band (excluding obs column).
            primary_band_w = plan.canvas_w - (
                self.node_w + self.h_gap if observability else 0
            )
            x = max(MARGIN_X, (primary_band_w - row_width) // 2)
            for c in row:
                plan.boxes[c.id] = Box(x=x, y=y, w=self.node_w, h=self.node_h)
                x += self.node_w + self.h_gap
            y += self.node_h + self.v_gap

        # Observability stacked on the right edge.
        if observability:
            ox = plan.canvas_w - MARGIN_X - self.node_w
            oy = MARGIN_Y
            for c in observability:
                plan.boxes[c.id] = Box(x=ox, y=oy, w=self.node_w, h=self.node_h)
                oy += self.node_h + 20

        return plan
