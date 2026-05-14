"""LLM client interface plus a deterministic stub.

The stub lets the rest of the pipeline run, be tested, and be demoed without
network calls or API keys. Drop in a real client (Anthropic, Vertex/Gemini) by
implementing `LLMClient.complete` and passing it to `LeadArchitect(llm=...)`.

The stub recognises a handful of keyword patterns in the requirement and emits
a structured intent dict that downstream subagents consume.  It is a
"first-draft architect" - good enough to demonstrate the pipeline end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Intent:
    """Structured interpretation of a free-text requirement."""

    title: str
    workload: str   # "web", "stream", "batch", "ml", "general"
    scale: str      # "small", "medium", "large", "global"
    latency_sensitive: bool = False
    write_heavy: bool = False
    read_heavy: bool = False
    global_consistency: bool = False
    high_availability: bool = False
    compliance: list[str] = field(default_factory=list)
    budget: str | None = None
    provider: str = "aws"


class LLMClient(Protocol):
    def interpret(self, requirement: str) -> Intent:  # pragma: no cover - interface
        ...

    def complete(self, prompt: str) -> str:  # pragma: no cover - interface
        ...


class StubLLM:
    """Deterministic, keyword-driven stub.

    Returns the same Intent for the same requirement, which keeps tests and
    diagrams reproducible.
    """

    def interpret(self, requirement: str) -> Intent:
        text = requirement.lower()

        workload = "general"
        if any(k in text for k in ("video", "stream", "pub/sub", "pubsub", "kafka", "real-time", "realtime")):
            workload = "stream"
        elif any(k in text for k in ("batch", "etl", "warehouse", "analytics")):
            workload = "batch"
        elif any(k in text for k in ("ml", "model", "inference", "ai/ml")):
            workload = "ml"
        elif any(k in text for k in ("web", "api", "saas", "app", "site", "users")):
            workload = "web"

        scale = "medium"
        if any(k in text for k in ("global", "worldwide", "multi-region")):
            scale = "global"
        elif any(k in text for k in ("million", "billion", "high scale", "high-scale", "10m", "100m")):
            scale = "large"
        elif any(k in text for k in ("small", "prototype", "mvp")):
            scale = "small"

        latency = any(k in text for k in ("low-latency", "low latency", "<100ms", "p99", "real-time", "realtime"))
        write_heavy = any(k in text for k in ("write-heavy", "ingest", "ingestion", "high write"))
        read_heavy = any(k in text for k in ("read-heavy", "many reads", "high read"))
        global_consistency = "consistent" in text and "global" in text
        ha = any(k in text for k in ("high availability", "ha", "always on", "always-on", "99.99"))

        compliance: list[str] = []
        for tag in ("hipaa", "pci", "soc2", "gdpr", "iso27001"):
            if tag in text:
                compliance.append(tag.upper())

        budget = None
        for token in text.split():
            if token.startswith("$"):
                budget = token
                break

        provider = "aws"
        if "gcp" in text or "google cloud" in text:
            provider = "gcp"
        elif "azure" in text:
            provider = "azure"

        # Title: first 60 chars of requirement, prettified.
        title = requirement.strip().splitlines()[0][:60].rstrip(".")
        if not title:
            title = "Untitled Architecture"

        return Intent(
            title=title,
            workload=workload,
            scale=scale,
            latency_sensitive=latency,
            write_heavy=write_heavy,
            read_heavy=read_heavy,
            global_consistency=global_consistency,
            high_availability=ha,
            compliance=compliance,
            budget=budget,
            provider=provider,
        )

    def complete(self, prompt: str) -> str:
        # Stub: echo a deterministic short response.  Real clients would call out.
        return f"[stub-llm reply to: {prompt[:80]}...]"
