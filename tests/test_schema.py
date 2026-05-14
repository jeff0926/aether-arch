import pytest
from pydantic import ValidationError

from aether.schemas.architecture import (
    Architecture,
    Component,
    ComponentKind,
    Connection,
    Tier,
)


def _arch(**overrides):
    components = overrides.pop("components", [
        Component(id="a", name="A", kind=ComponentKind.LOAD_BALANCER),
        Component(id="b", name="B", kind=ComponentKind.LAMBDA),
    ])
    connections = overrides.pop("connections", [Connection(source="a", target="b")])
    return Architecture(
        title="t",
        requirement="r",
        components=components,
        connections=connections,
        **overrides,
    )


def test_default_tier_resolution():
    c = Component(id="x", name="X", kind=ComponentKind.DATABASE_SQL)
    assert c.resolved_tier == Tier.DATA


def test_duplicate_ids_rejected():
    with pytest.raises(ValidationError):
        Architecture(
            title="t", requirement="r",
            components=[
                Component(id="x", name="X", kind=ComponentKind.LAMBDA),
                Component(id="x", name="Y", kind=ComponentKind.CACHE),
            ],
        )


def test_invalid_connection_target():
    arch = _arch(connections=[Connection(source="a", target="nope")])
    with pytest.raises(ValueError):
        arch.validate_connections()


def test_whitespace_id_rejected():
    with pytest.raises(ValidationError):
        Component(id="bad id", name="X", kind=ComponentKind.LAMBDA)
