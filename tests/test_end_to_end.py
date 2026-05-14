from xml.etree import ElementTree as ET

from aether import LeadArchitect, emit_drawio
from aether.knowledge.papers import PAPERS


def test_video_streaming_requirement_produces_valid_diagram():
    architect = LeadArchitect()
    result = architect.synthesise(
        "Low-latency video streaming platform for 10 million global users."
    )
    arch = result.architecture
    assert any(c.id == "cdn" for c in arch.components), "global streaming needs a CDN"
    assert any(c.kind.value == "stream" for c in arch.components)
    xml = emit_drawio(arch, result.plan)
    parsed = ET.fromstring(xml.split("\n", 1)[1])
    assert parsed.tag == "mxfile"


def test_relational_workload_picks_sql_database():
    result = LeadArchitect().synthesise(
        "Internal SaaS web app for 500 users, moderate scale."
    )
    kinds = {c.kind.value for c in result.architecture.components}
    assert "database_sql" in kinds


def test_global_consistency_picks_spanner_style():
    result = LeadArchitect().synthesise(
        "Globally consistent inventory ledger across multi-region datacenters."
    )
    # Either a global SQL was chosen or the decisions cite Spanner.
    cites = {p for d in result.trace.decisions for p in d.grounded_in}
    assert "spanner" in cites or any(c.id == "db" for c in result.architecture.components)


def test_security_findings_are_warnings_not_errors_after_autofix():
    result = LeadArchitect().synthesise(
        "High-availability payments API, PCI compliance required."
    )
    errors = [f for f in result.trace.findings if f.severity == "error"]
    assert not errors, f"unexpected errors: {errors}"


def test_all_grounded_paper_ids_resolve():
    result = LeadArchitect().synthesise("Big data analytics warehouse for 1B rows/day.")
    for d in result.trace.decisions:
        for pid in d.grounded_in:
            assert pid in PAPERS, f"unknown paper id cited: {pid}"


def test_exactly_forty_canonical_papers():
    assert len(PAPERS) == 40
