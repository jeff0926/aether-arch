from aether.schemas.architecture import ComponentKind
from aether.style_registry import edge_style, style_for


def test_aws_lambda_style_has_shape_and_fill():
    s = style_for(ComponentKind.LAMBDA, "aws")
    assert "shape=mxgraph.aws4" in s
    assert "fillColor=#" in s
    assert "strokeColor=" in s


def test_unknown_provider_falls_back_to_generic():
    s = style_for(ComponentKind.LAMBDA, "ibm")
    assert "rounded=1" in s


def test_every_kind_has_style_for_every_provider():
    for kind in ComponentKind:
        for provider in ("aws", "gcp", "azure", "generic"):
            s = style_for(kind, provider)
            assert s, f"missing style for {kind} on {provider}"


def test_edge_style_solid_vs_dashed():
    assert "dashed" not in edge_style("solid")
    assert "dashed=1" in edge_style("dashed")
