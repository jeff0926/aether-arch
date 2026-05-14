"""Lead Architect orchestrator.

Implements the four-step Reasoning Loop described in the PDF:

  1. Perception      - ingest the requirement
  2. Reasoning       - decompose into sub-problems (storage / edge / compute /
                       messaging / observability)
  3. Grounding       - cite the canonical papers behind each decision
  4. Action          - synthesise the Architecture object, run Security
                       Auditor, hand off to the Layout subagent

The orchestrator returns a `ReasoningTrace` so callers (the CLI, future HITL UI)
can show *why* a particular component was chosen.  This is the auditable
"Agent Gateway" trail the PDF requires.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aether.agents.llm import Intent, LLMClient, StubLLM
from aether.agents.subagents import (
    LayoutSubagent,
    SecurityFinding,
    SecuritySubagent,
    design_storage,
)
from aether.layout.tiered import LayoutPlan
from aether.schemas.architecture import (
    Architecture,
    Component,
    ComponentKind,
    Connection,
    Constraint,
    Decision,
)


@dataclass
class ReasoningTrace:
    intent: Intent
    decisions: list[Decision] = field(default_factory=list)
    findings: list[SecurityFinding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class SynthesisResult:
    architecture: Architecture
    plan: LayoutPlan
    trace: ReasoningTrace


class LeadArchitect:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or StubLLM()
        self.security = SecuritySubagent()
        self.layout = LayoutSubagent()

    # --- main entrypoint -------------------------------------------------

    def synthesise(self, requirement: str) -> SynthesisResult:
        trace = ReasoningTrace(intent=self._perceive(requirement))
        components, connections, constraints = self._reason(trace.intent, trace)
        arch = Architecture(
            title=trace.intent.title,
            requirement=requirement,
            components=components,
            connections=connections,
            constraints=constraints,
            decisions=list(trace.decisions),
        )

        # Auto-repair obvious issues, then audit what's left.
        arch = self.security.autofix(arch)
        trace.findings = self.security.audit(arch, compliance=trace.intent.compliance)

        plan = self.layout.plan(arch)
        return SynthesisResult(architecture=arch, plan=plan, trace=trace)

    # --- steps -----------------------------------------------------------

    def _perceive(self, requirement: str) -> Intent:
        return self.llm.interpret(requirement)

    def _reason(
        self, intent: Intent, trace: ReasoningTrace
    ) -> tuple[list[Component], list[Connection], list[Constraint]]:
        components: list[Component] = []
        connections: list[Connection] = []
        constraints: list[Constraint] = []

        # --- Entry tier ---------------------------------------------------
        components.append(Component(
            id="user", name="End User",
            kind=ComponentKind.CLIENT, provider=intent.provider,
            public=True,
        ))
        components.append(Component(
            id="dns", name="DNS",
            kind=ComponentKind.DNS, provider=intent.provider, public=True,
        ))
        if intent.scale in ("large", "global") or intent.workload == "stream":
            components.append(Component(
                id="cdn", name="CDN",
                kind=ComponentKind.CDN, provider=intent.provider, public=True,
            ))
            trace.decisions.append(Decision(
                summary="CDN at the edge to absorb global read traffic",
                rationale="End-to-end argument: push delivery to the edges of the system.",
                grounded_in=["e2e", "tail"],
            ))

        components.append(Component(
            id="waf", name="WAF",
            kind=ComponentKind.WAF, provider=intent.provider,
        ))

        # --- Web tier -----------------------------------------------------
        components.append(Component(
            id="lb", name="Load Balancer",
            kind=ComponentKind.LOAD_BALANCER, provider=intent.provider,
            multi_region=intent.scale == "global",
        ))
        trace.decisions.append(Decision(
            summary="Front-end load balancer for horizontal scaling",
            rationale="Tail-latency mitigation via hedged requests across replicas.",
            grounded_in=["tail"],
        ))

        if intent.workload in ("web", "ml", "general"):
            components.append(Component(
                id="api", name="API Gateway",
                kind=ComponentKind.API_GATEWAY, provider=intent.provider,
            ))

        # --- App tier -----------------------------------------------------
        if intent.scale in ("large", "global") or intent.workload == "ml":
            components.append(Component(
                id="app", name="Kubernetes Workloads",
                kind=ComponentKind.KUBERNETES, provider=intent.provider,
            ))
            trace.decisions.append(Decision(
                summary="Container orchestrator hosts the application tier",
                rationale="Declarative control loop manages pods/replicasets at scale.",
                grounded_in=["borg_k8s", "k8s_book", "k8s_history"],
            ))
        else:
            components.append(Component(
                id="app", name="Serverless Functions",
                kind=ComponentKind.LAMBDA, provider=intent.provider,
            ))
            trace.decisions.append(Decision(
                summary="Serverless compute for the app tier",
                rationale="SEDA-style stages with auto-scale; no idle capacity to fund.",
                grounded_in=["seda"],
            ))

        # --- Messaging (stream workloads or write-heavy) -----------------
        if intent.workload == "stream" or intent.write_heavy:
            components.append(Component(
                id="bus", name="Event Bus",
                kind=ComponentKind.STREAM, provider=intent.provider, encrypted=True,
            ))
            trace.decisions.append(Decision(
                summary="Durable partitioned log between producers and consumers",
                rationale="Kafka-style persistence decouples write rate from consumer rate.",
                grounded_in=["kafka", "corfu"],
            ))

        # --- Storage tier (delegated to Storage subagent) ---------------
        storage_components, storage_decisions = design_storage(intent)
        components.extend(storage_components)
        trace.decisions.extend(storage_decisions)

        # --- Observability ----------------------------------------------
        components.append(Component(
            id="logs", name="Logs",
            kind=ComponentKind.LOGGING, provider=intent.provider,
        ))
        components.append(Component(
            id="trace", name="Distributed Tracing",
            kind=ComponentKind.TRACING, provider=intent.provider,
        ))
        trace.decisions.append(Decision(
            summary="Dapper-style tracing across the request path",
            rationale="Trace IDs make multi-service diagnosis tractable.",
            grounded_in=["dapper"],
        ))

        # --- Wire connections (only between ids that exist) --------------
        ids = {c.id for c in components}

        def link(src: str, dst: str, label: str | None = None) -> None:
            if src in ids and dst in ids:
                connections.append(Connection(source=src, target=dst, label=label))

        link("user", "dns")
        link("dns", "cdn" if "cdn" in ids else "waf")
        if "cdn" in ids:
            link("cdn", "waf")
        link("waf", "lb")
        link("lb", "api" if "api" in ids else "app")
        if "api" in ids:
            link("api", "app")
        if "bus" in ids:
            link("app", "bus")
            for sid in ("db", "log", "hot_store", "warehouse"):
                link("bus", sid)
        for sid in ("db", "cache", "blob", "warehouse", "lake", "hot_store", "log"):
            link("app", sid)
        link("app", "logs")
        link("app", "trace")

        # --- Constraints captured from the requirement ------------------
        if intent.budget:
            constraints.append(Constraint(kind="budget", value=intent.budget))
        if intent.latency_sensitive:
            constraints.append(Constraint(kind="latency", value="low"))
        if intent.high_availability:
            constraints.append(Constraint(kind="availability", value="high"))
        for c in intent.compliance:
            constraints.append(Constraint(kind="compliance", value=c))

        trace.notes.append(
            f"workload={intent.workload}, scale={intent.scale}, provider={intent.provider}"
        )
        return components, connections, constraints
