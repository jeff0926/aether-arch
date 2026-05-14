from xml.etree import ElementTree as ET

from aether.emitter.mxgraph import emit_drawio, emit_mxgraph_model
from aether.schemas.architecture import (
    Architecture,
    Component,
    ComponentKind,
    Connection,
)


def _three_tier() -> Architecture:
    return Architecture(
        title="Three Tier",
        requirement="r",
        components=[
            Component(id="lb", name="LB", kind=ComponentKind.LOAD_BALANCER),
            Component(id="app", name="App", kind=ComponentKind.LAMBDA),
            Component(id="db", name="DB", kind=ComponentKind.DATABASE_SQL, encrypted=True),
        ],
        connections=[
            Connection(source="lb", target="app"),
            Connection(source="app", target="db"),
        ],
    )


def test_root_cell_and_default_layer_present():
    """PDF failure mode #1: missing id=0 and id=1 yields blank canvas."""
    model = emit_mxgraph_model(_three_tier())
    root = model.find("root")
    ids = [c.get("id") for c in root.findall("mxCell")]
    assert "0" in ids
    assert "1" in ids
    layer = next(c for c in root.findall("mxCell") if c.get("id") == "1")
    assert layer.get("parent") == "0"


def test_every_edge_has_relative_geometry():
    """PDF failure mode #2: edges without relative=1 geometry don't render."""
    model = emit_mxgraph_model(_three_tier())
    root = model.find("root")
    edges = [c for c in root.findall("mxCell") if c.get("edge") == "1"]
    assert len(edges) == 2
    for e in edges:
        geom = e.find("mxGeometry")
        assert geom is not None, "edge missing child mxGeometry"
        assert geom.get("relative") == "1"
        assert geom.get("as") == "geometry"


def test_every_vertex_has_geometry_with_coords():
    model = emit_mxgraph_model(_three_tier())
    root = model.find("root")
    verts = [c for c in root.findall("mxCell") if c.get("vertex") == "1"]
    assert len(verts) == 3
    for v in verts:
        geom = v.find("mxGeometry")
        assert geom is not None
        assert int(geom.get("width")) > 0
        assert int(geom.get("height")) > 0
        assert geom.get("x") is not None
        assert geom.get("y") is not None


def test_drawio_wrapper_is_parseable_xml():
    xml = emit_drawio(_three_tier())
    parsed = ET.fromstring(xml.split("\n", 1)[1])
    assert parsed.tag == "mxfile"
    assert parsed.find("diagram") is not None


def test_tiered_layout_orders_top_to_bottom():
    model = emit_mxgraph_model(_three_tier())
    root = model.find("root")
    coords = {}
    for cell in root.findall("mxCell"):
        if cell.get("vertex") == "1":
            geom = cell.find("mxGeometry")
            coords[cell.get("id")] = int(geom.get("y"))
    # Web tier (lb) above app tier (app) above data tier (db).
    assert coords["c-lb"] < coords["c-app"] < coords["c-db"]
