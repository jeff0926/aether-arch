"""Non-lossy intermediate schema for architectures.

This Pydantic model is the canonical machine representation that flows between
agents and into the draw.io emitter. YAML is accepted as human input but is
always normalized to this typed form before processing (see PDF: JSON for
machine exchange, YAML for human ingestion).
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComponentKind(str, Enum):
    # Compute
    COMPUTE = "compute"
    LAMBDA = "lambda"
    CONTAINER = "container"
    KUBERNETES = "kubernetes"
    # Storage
    DATABASE_SQL = "database_sql"
    DATABASE_NOSQL = "database_nosql"
    OBJECT_STORE = "object_store"
    CACHE = "cache"
    DATA_WAREHOUSE = "data_warehouse"
    # Networking
    LOAD_BALANCER = "load_balancer"
    CDN = "cdn"
    API_GATEWAY = "api_gateway"
    DNS = "dns"
    # Messaging
    QUEUE = "queue"
    STREAM = "stream"
    # Security
    WAF = "waf"
    IAM = "iam"
    SECRETS = "secrets"
    # Observability
    LOGGING = "logging"
    MONITORING = "monitoring"
    TRACING = "tracing"
    # Client / external
    CLIENT = "client"
    EXTERNAL = "external"


class Tier(str, Enum):
    """Logical row in a tiered architecture diagram (PDF Layout Rule)."""

    CLIENT = "client"
    EDGE = "edge"
    WEB = "web"
    APP = "app"
    DATA = "data"
    OBSERVABILITY = "observability"


# Map every ComponentKind to its default tier. The Layout subagent can override.
DEFAULT_TIER: dict[ComponentKind, Tier] = {
    ComponentKind.CLIENT: Tier.CLIENT,
    ComponentKind.EXTERNAL: Tier.CLIENT,
    ComponentKind.CDN: Tier.EDGE,
    ComponentKind.DNS: Tier.EDGE,
    ComponentKind.WAF: Tier.EDGE,
    ComponentKind.LOAD_BALANCER: Tier.WEB,
    ComponentKind.API_GATEWAY: Tier.WEB,
    ComponentKind.COMPUTE: Tier.APP,
    ComponentKind.LAMBDA: Tier.APP,
    ComponentKind.CONTAINER: Tier.APP,
    ComponentKind.KUBERNETES: Tier.APP,
    ComponentKind.QUEUE: Tier.APP,
    ComponentKind.STREAM: Tier.APP,
    ComponentKind.DATABASE_SQL: Tier.DATA,
    ComponentKind.DATABASE_NOSQL: Tier.DATA,
    ComponentKind.OBJECT_STORE: Tier.DATA,
    ComponentKind.CACHE: Tier.DATA,
    ComponentKind.DATA_WAREHOUSE: Tier.DATA,
    ComponentKind.IAM: Tier.OBSERVABILITY,
    ComponentKind.SECRETS: Tier.OBSERVABILITY,
    ComponentKind.LOGGING: Tier.OBSERVABILITY,
    ComponentKind.MONITORING: Tier.OBSERVABILITY,
    ComponentKind.TRACING: Tier.OBSERVABILITY,
}


class Component(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Stable identifier referenced by connections.")
    name: str
    kind: ComponentKind
    provider: Literal["aws", "gcp", "azure", "generic"] = "aws"
    tier: Tier | None = None
    # Metadata the Security Auditor inspects.
    encrypted: bool = False
    public: bool = False
    multi_region: bool = False
    notes: str | None = None

    @field_validator("id")
    @classmethod
    def _id_token(cls, v: str) -> str:
        if not v or any(c.isspace() for c in v):
            raise ValueError("component id must be non-empty and contain no whitespace")
        return v

    @property
    def resolved_tier(self) -> Tier:
        return self.tier or DEFAULT_TIER.get(self.kind, Tier.APP)


class Connection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    target: str
    label: str | None = None
    protocol: str | None = None
    style: Literal["solid", "dashed"] = "solid"


class Constraint(BaseModel):
    """A requirement-derived constraint, e.g. budget, latency, compliance."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["budget", "latency", "throughput", "availability", "compliance", "other"]
    value: str


class Decision(BaseModel):
    """An architectural decision with a grounding citation.

    The PDF stresses that every decision should reference a canonical paper or
    principle. `grounded_in` holds the paper id from aether.knowledge.papers.
    """

    model_config = ConfigDict(extra="forbid")

    summary: str
    rationale: str
    grounded_in: list[str] = Field(default_factory=list)


class Architecture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    requirement: str
    components: list[Component]
    connections: list[Connection] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)

    @field_validator("components")
    @classmethod
    def _unique_ids(cls, components: list[Component]) -> list[Component]:
        seen: set[str] = set()
        for c in components:
            if c.id in seen:
                raise ValueError(f"duplicate component id: {c.id}")
            seen.add(c.id)
        return components

    def validate_connections(self) -> None:
        """Ensure every connection references existing component ids."""
        ids = {c.id for c in self.components}
        for conn in self.connections:
            if conn.source not in ids:
                raise ValueError(f"connection source not found: {conn.source}")
            if conn.target not in ids:
                raise ValueError(f"connection target not found: {conn.target}")

    def component(self, cid: str) -> Component:
        for c in self.components:
            if c.id == cid:
                return c
        raise KeyError(cid)
