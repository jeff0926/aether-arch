# aether-arch

**An agentic system for architectural solutions.** Turn a free-text requirement
into a validated architecture and a high-fidelity `.drawio` diagram, with every
design decision grounded in the canonical distributed-systems literature.

This is the implementation of the framework described in
*"Architectural Synthesis of Autonomous Systems: A Framework for Agentic
Principal Solution Design Leveraging Canonical Distributed Systems and
Programmatic Schemas"*.

## What it does

```
$ aether build "Low-latency video streaming platform for 10 million global users, HIPAA, budget $50k/month"

=== Low-latency video streaming platform for 10 million global u ===
Components: 11    Connections: 12
Provider:   aws    Workload: stream    Scale: global

Decisions (grounded in canonical papers):
  - CDN at the edge to absorb global read traffic  [e2e, tail]
      rationale: End-to-end argument: push delivery to the edges of the system.
  - Container orchestrator hosts the application tier  [borg_k8s, k8s_book]
      rationale: Declarative control loop manages pods/replicasets at scale.
  - Durable partitioned log between producers and consumers  [kafka, corfu]
      rationale: Kafka-style persistence decouples write rate from consumer rate.
  ...

Security audit:
  WARN (bus): HIPAA: Event Bus should be multi-region for durability.

Wrote video.drawio
Wrote video.json
```

Open `video.drawio` directly in [diagrams.net](https://app.diagrams.net) - the
file contains valid mxGraphModel XML with AWS / GCP / Azure stencil icons.

## Pipeline

```
requirement (free text)
        |
        v
+-----------------+
| Lead Architect  |   <-- 4-step Reasoning Loop
|  1 Perception   |
|  2 Reasoning    |---> subagents: Storage / Layout / Security
|  3 Grounding    |---> 40 canonical papers (aether.knowledge.papers)
|  4 Action       |
+-----------------+
        |
        v
Architecture (Pydantic / JSON Schema)  <-- non-lossy intermediate
        |
        +--> Security Auditor  (autofix + findings)
        |
        +--> Layout Subagent   (tiered: web > app > data, A4 canvas)
        |
        v
mxGraph XML emitter  --> .drawio file
```

## Key implementation guarantees

The PDF identifies two failure modes in AI-generated draw.io files; the emitter
defends against both with explicit tests:

1. **Mandatory structural cells.** Every diagram contains `<mxCell id="0"/>`
   and `<mxCell id="1" parent="0"/>` - without these the canvas opens blank.
   See `tests/test_emitter.py::test_root_cell_and_default_layer_present`.
2. **Edge geometry.** Every connector has a child
   `<mxGeometry relative="1" as="geometry"/>` - without `relative="1"` the
   lines don't render. See
   `tests/test_emitter.py::test_every_edge_has_relative_geometry`.

Layout follows the PDF's rules: horizontal spacing 40-60 px within a tier,
vertical spacing 80-120 px between tiers, A4 landscape canvas 1169x827 (the
canvas auto-grows for larger diagrams).

## Why decisions are grounded

Every `Decision` carries a `grounded_in: list[str]` of paper IDs from the
40-paper canonical library (`aether.knowledge.papers.PAPERS`). The Lead
Architect won't pick global SQL without citing Spanner+CAP, won't choose a
masterless NoSQL without citing Dynamo+Cassandra, won't add a CDN without
citing the End-to-End argument.

Inspect the library:

```
aether papers                # list all 40
aether papers --topic consensus
aether explain raft
```

## Installation

```
pip install -e ".[dev]"
pytest                # 23 tests
```

Python 3.10+.

## Architecture decisions baked into this codebase

| Concern | Choice | Source |
| --- | --- | --- |
| Intermediate schema | JSON (Pydantic) for machine; YAML for human input | PDF Non-Lossy Intermediate Schemas |
| Diagram format | draw.io mxGraphModel XML | PDF mxGraph XML Structure |
| Icon library | AWS aws4, GCP gcp2, Azure azure2 stencils | PDF High-Fidelity Styling |
| Layout | Tiered rows: Client / Edge / Web / App / Data | PDF Logic for Automated Diagram Generation |
| Security pass | Auto-fix obvious issues; warn HITL on trade-offs | PDF Human-in-the-Loop |
| LLM | Pluggable `LLMClient` protocol; stub for offline use | (this build chose stub) |

## Swapping in a real LLM

`aether.agents.llm.LLMClient` is a `Protocol` with two methods. To use Claude:

```python
import anthropic
from aether.agents.llm import Intent, LLMClient

class ClaudeLLM:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def interpret(self, requirement: str) -> Intent:
        # Ask Claude to return a JSON object matching Intent.
        ...

    def complete(self, prompt: str) -> str:
        msg = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

LeadArchitect(llm=ClaudeLLM()).synthesise("...")
```

Same shape works for Vertex AI / Gemini.

## Layout

```
aether/
  schemas/architecture.py   non-lossy Pydantic model
  style_registry.py         (kind, provider) -> mxGraph style string
  layout/tiered.py          A4 canvas, tiered row planner
  emitter/mxgraph.py        .drawio XML emitter (guards against the two failure modes)
  knowledge/papers.py       40 canonical papers
  agents/
    llm.py                  LLMClient protocol + StubLLM
    lead_architect.py       4-step Reasoning Loop orchestrator
    subagents/
      storage.py            picks data tier, cites Aurora/Cassandra/Spanner/...
      security.py           encryption + isolation audit + autofix
      layout.py             wraps TieredLayout
  cli.py                    `aether build` / `papers` / `explain`
tests/                      23 tests, no network
```
