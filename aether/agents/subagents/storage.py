"""Storage subagent.

Picks data-tier components and justifies them with citations to the canonical
papers (Aurora, Cassandra, Spanner, S3, etc.) per the PDF's grounding step.
"""

from __future__ import annotations

from aether.agents.llm import Intent
from aether.schemas.architecture import Component, ComponentKind, Decision


def design_storage(intent: Intent) -> tuple[list[Component], list[Decision]]:
    components: list[Component] = []
    decisions: list[Decision] = []

    if intent.workload == "batch":
        components.append(Component(
            id="warehouse", name="Data Warehouse",
            kind=ComponentKind.DATA_WAREHOUSE, provider=intent.provider,
            encrypted=True, multi_region=intent.scale == "global",
        ))
        components.append(Component(
            id="lake", name="Object Store",
            kind=ComponentKind.OBJECT_STORE, provider=intent.provider,
            encrypted=True,
        ))
        decisions.append(Decision(
            summary="Storage/compute separation for the analytics tier",
            rationale="Independent scaling of ingest and query, per Snowflake.",
            grounded_in=["snowflake", "hive"],
        ))
        return components, decisions

    if intent.workload == "stream":
        components.append(Component(
            id="log", name="Event Log",
            kind=ComponentKind.STREAM, provider=intent.provider,
            encrypted=True, multi_region=intent.scale == "global",
        ))
        components.append(Component(
            id="hot_store", name="Hot Store",
            kind=ComponentKind.DATABASE_NOSQL, provider=intent.provider,
            encrypted=True,
        ))
        decisions.append(Decision(
            summary="Partitioned log as the system of record",
            rationale="Kafka-style pull persistence supports multiple independent consumers.",
            grounded_in=["kafka", "corfu"],
        ))
        if intent.write_heavy:
            decisions.append(Decision(
                summary="LSM-tree-backed NoSQL for write-heavy hot path",
                rationale="Append-then-merge beats in-place updates at this write rate.",
                grounded_in=["lsm", "cassandra"],
            ))
        return components, decisions

    # web / general / ml all default to a relational primary + cache.
    if intent.global_consistency:
        components.append(Component(
            id="db", name="Global SQL",
            kind=ComponentKind.DATABASE_SQL, provider=intent.provider,
            encrypted=True, multi_region=True,
        ))
        decisions.append(Decision(
            summary="Externally consistent global database",
            rationale="Spanner-style TrueTime gives the transactional ordering the requirement demands.",
            grounded_in=["spanner", "cap"],
        ))
    elif intent.high_availability or intent.scale in ("large", "global"):
        components.append(Component(
            id="db", name="Decentralized NoSQL",
            kind=ComponentKind.DATABASE_NOSQL, provider=intent.provider,
            encrypted=True, multi_region=intent.scale == "global",
        ))
        decisions.append(Decision(
            summary="Masterless NoSQL chosen for availability under partition",
            rationale="Dynamo+Bigtable lineage; sloppy quorums favor writes during AZ loss.",
            grounded_in=["dynamo", "dynamo_avail", "cassandra", "cap"],
        ))
    else:
        components.append(Component(
            id="db", name="Relational DB",
            kind=ComponentKind.DATABASE_SQL, provider=intent.provider,
            encrypted=True,
        ))
        decisions.append(Decision(
            summary="Log-as-database relational store",
            rationale="Aurora separates compute from log-structured storage; read replicas at zero lag.",
            grounded_in=["aurora"],
        ))

    if intent.latency_sensitive or intent.read_heavy:
        components.append(Component(
            id="cache", name="Cache",
            kind=ComponentKind.CACHE, provider=intent.provider,
            encrypted=True,
        ))
        decisions.append(Decision(
            summary="In-memory cache fronts the database",
            rationale="Bound tail latency; hedged reads from the cache layer.",
            grounded_in=["tail"],
        ))

    components.append(Component(
        id="blob", name="Object Store",
        kind=ComponentKind.OBJECT_STORE, provider=intent.provider,
        encrypted=True,
    ))
    return components, decisions
