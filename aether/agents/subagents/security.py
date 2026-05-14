"""Security Auditor subagent.

Per the PDF: every generated architecture is automatically audited for
EncryptionSpec, network isolation, and audit trails. Findings either block the
design (severity=error) or surface for HITL review (severity=warn).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from aether.schemas.architecture import Architecture, Component, ComponentKind


@dataclass
class SecurityFinding:
    severity: Literal["error", "warn", "info"]
    component_id: str | None
    message: str


# Component kinds that must always be encrypted at rest.
_MUST_ENCRYPT = {
    ComponentKind.DATABASE_SQL,
    ComponentKind.DATABASE_NOSQL,
    ComponentKind.OBJECT_STORE,
    ComponentKind.CACHE,
    ComponentKind.DATA_WAREHOUSE,
    ComponentKind.STREAM,
    ComponentKind.QUEUE,
}

# Component kinds that must never be public.
_MUST_BE_PRIVATE = {
    ComponentKind.DATABASE_SQL,
    ComponentKind.DATABASE_NOSQL,
    ComponentKind.CACHE,
    ComponentKind.DATA_WAREHOUSE,
}


class SecuritySubagent:
    def audit(self, arch: Architecture, compliance: list[str] | None = None) -> list[SecurityFinding]:
        compliance = compliance or []
        findings: list[SecurityFinding] = []

        for c in arch.components:
            if c.kind in _MUST_ENCRYPT and not c.encrypted:
                findings.append(SecurityFinding(
                    severity="error",
                    component_id=c.id,
                    message=f"{c.name} stores data at rest but is not encrypted (EncryptionSpec missing).",
                ))
            if c.kind in _MUST_BE_PRIVATE and c.public:
                findings.append(SecurityFinding(
                    severity="error",
                    component_id=c.id,
                    message=f"{c.name} is exposed publicly; place behind PrivateServiceConnect.",
                ))

        # Observability requirement: at least one logging or tracing component.
        kinds = {c.kind for c in arch.components}
        if not (kinds & {ComponentKind.LOGGING, ComponentKind.TRACING, ComponentKind.MONITORING}):
            findings.append(SecurityFinding(
                severity="warn",
                component_id=None,
                message="No observability component (logging/tracing/monitoring) present; add for audit trails.",
            ))

        # Edge protection requirement: public-facing systems should have WAF or LB.
        edge = kinds & {ComponentKind.WAF, ComponentKind.LOAD_BALANCER, ComponentKind.API_GATEWAY, ComponentKind.CDN}
        if not edge:
            findings.append(SecurityFinding(
                severity="warn",
                component_id=None,
                message="No edge protection (WAF / LB / API GW / CDN); public traffic reaches origin directly.",
            ))

        if "HIPAA" in compliance:
            for c in arch.components:
                if c.kind in _MUST_ENCRYPT and not c.multi_region:
                    findings.append(SecurityFinding(
                        severity="warn",
                        component_id=c.id,
                        message=f"HIPAA: {c.name} should be multi-region for durability.",
                    ))

        return findings

    @staticmethod
    def autofix(arch: Architecture) -> Architecture:
        """Repair the architecture in-place by tightening defaults.

        This is the HITL pre-step: the agent corrects obvious issues so the
        human reviewer only sees genuinely ambiguous trade-offs.
        """
        fixed_components: list[Component] = []
        for c in arch.components:
            if c.kind in _MUST_ENCRYPT and not c.encrypted:
                c = c.model_copy(update={"encrypted": True})
            if c.kind in _MUST_BE_PRIVATE and c.public:
                c = c.model_copy(update={"public": False})
            fixed_components.append(c)
        return arch.model_copy(update={"components": fixed_components})
