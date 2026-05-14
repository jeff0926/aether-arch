"""draw.io / mxGraph XML emitter.

The PDF identifies two failure modes in AI-generated diagrams that this module
defends against:

1.  Missing root cell (id="0") and default layer cell (id="1") -> blank canvas.
2.  Edges without a child <mxGeometry relative="1"/> -> connectors don't render.

We produce the .drawio container format that draw.io reads natively:

    <mxfile host="aether-arch">
      <diagram name="...">
        <mxGraphModel ...>
          <root>
            <mxCell id="0"/>
            <mxCell id="1" parent="0"/>
            ...vertices/edges...
          </root>
        </mxGraphModel>
      </diagram>
    </mxfile>
"""

from __future__ import annotations

from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from aether.layout.tiered import LayoutPlan, TieredLayout
from aether.schemas.architecture import Architecture
from aether.style_registry import edge_style, style_for


def emit_mxgraph_model(arch: Architecture, plan: LayoutPlan | None = None) -> ET.Element:
    """Return the <mxGraphModel> element for the architecture."""
    arch.validate_connections()
    plan = plan or TieredLayout().plan(arch)

    model = ET.Element(
        "mxGraphModel",
        {
            "dx": str(plan.canvas_w),
            "dy": str(plan.canvas_h),
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(plan.canvas_w),
            "pageHeight": str(plan.canvas_h),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")

    # Mandatory structural cells.  Omitting these is the #1 cause of blank
    # canvases in AI-generated draw.io files (per PDF).
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # Vertices.
    for comp in arch.components:
        box = plan.get(comp.id)
        style = style_for(comp.kind, comp.provider)
        # Make label more readable beneath stencil glyphs.
        style += "verticalLabelPosition=bottom;verticalAlign=top;align=center;"
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": f"c-{comp.id}",
                "value": comp.name,
                "style": style,
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": str(box.x),
                "y": str(box.y),
                "width": str(box.w),
                "height": str(box.h),
                "as": "geometry",
            },
        )

    # Edges.  The relative="1" attribute on child mxGeometry is mandatory.
    for idx, conn in enumerate(arch.connections):
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": f"e-{idx}",
                "value": conn.label or "",
                "style": edge_style(conn.style),
                "edge": "1",
                "parent": "1",
                "source": f"c-{conn.source}",
                "target": f"c-{conn.target}",
            },
        )
        ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})

    return model


def emit_drawio(arch: Architecture, plan: LayoutPlan | None = None) -> str:
    """Return a complete .drawio (mxfile) XML document as a string."""
    model = emit_mxgraph_model(arch, plan)

    mxfile = ET.Element(
        "mxfile",
        {
            "host": "aether-arch",
            "agent": "aether/0.1",
            "version": "24.0.0",
            "type": "device",
        },
    )
    diagram = ET.SubElement(
        mxfile,
        "diagram",
        {"id": "aether-diagram", "name": escape(arch.title)},
    )
    diagram.append(model)

    ET.indent(mxfile, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        mxfile, encoding="unicode"
    )
