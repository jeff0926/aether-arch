from aether.agents.subagents.security import SecuritySubagent
from aether.schemas.architecture import (
    Architecture,
    Component,
    ComponentKind,
    Connection,
)


def _arch(db_encrypted=False, db_public=False):
    return Architecture(
        title="t", requirement="r",
        components=[
            Component(id="lb", name="LB", kind=ComponentKind.LOAD_BALANCER),
            Component(id="db", name="DB", kind=ComponentKind.DATABASE_SQL,
                      encrypted=db_encrypted, public=db_public),
        ],
        connections=[Connection(source="lb", target="db")],
    )


def test_unencrypted_database_raises_error():
    findings = SecuritySubagent().audit(_arch(db_encrypted=False))
    errs = [f for f in findings if f.severity == "error"]
    assert any("not encrypted" in f.message for f in errs)


def test_public_database_raises_error():
    findings = SecuritySubagent().audit(_arch(db_encrypted=True, db_public=True))
    assert any(f.severity == "error" and "public" in f.message.lower() for f in findings)


def test_missing_observability_warns():
    arch = _arch(db_encrypted=True)
    findings = SecuritySubagent().audit(arch)
    assert any(f.severity == "warn" and "observability" in f.message.lower() for f in findings)


def test_autofix_encrypts_and_privatises():
    arch = _arch(db_encrypted=False, db_public=True)
    fixed = SecuritySubagent.autofix(arch)
    db = fixed.component("db")
    assert db.encrypted is True
    assert db.public is False
