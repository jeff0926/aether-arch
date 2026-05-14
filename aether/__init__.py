"""aether-arch: agentic system for architectural solutions."""

__version__ = "0.1.0"

from aether.schemas.architecture import Architecture, Component, Connection, ComponentKind
from aether.agents.lead_architect import LeadArchitect
from aether.emitter.mxgraph import emit_drawio

__all__ = [
    "Architecture",
    "Component",
    "Connection",
    "ComponentKind",
    "LeadArchitect",
    "emit_drawio",
]
