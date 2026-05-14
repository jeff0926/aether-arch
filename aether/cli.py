"""aether CLI.

    aether build "We need a low-latency video streaming platform" -o video.drawio

Produces:
  * a `.drawio` file ready to open in https://app.diagrams.net
  * a sibling `.json` with the validated Architecture (the non-lossy schema)
  * a console report of decisions + security findings (the HITL summary)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from aether.agents.lead_architect import LeadArchitect, SynthesisResult
from aether.emitter.mxgraph import emit_drawio


def _print_report(result: SynthesisResult) -> None:
    arch = result.architecture
    trace = result.trace
    click.echo(click.style(f"\n=== {arch.title} ===", bold=True))
    click.echo(f"Components: {len(arch.components)}    Connections: {len(arch.connections)}")
    click.echo(f"Provider:   {trace.intent.provider}    Workload: {trace.intent.workload}    Scale: {trace.intent.scale}")

    if trace.decisions:
        click.echo(click.style("\nDecisions (grounded in canonical papers):", bold=True))
        for d in trace.decisions:
            cites = f"  [{', '.join(d.grounded_in)}]" if d.grounded_in else ""
            click.echo(f"  - {d.summary}{cites}")
            click.echo(f"      rationale: {d.rationale}")

    if trace.findings:
        click.echo(click.style("\nSecurity audit:", bold=True))
        for f in trace.findings:
            colour = {"error": "red", "warn": "yellow", "info": "cyan"}[f.severity]
            tag = click.style(f.severity.upper(), fg=colour)
            target = f" ({f.component_id})" if f.component_id else ""
            click.echo(f"  {tag}{target}: {f.message}")
    else:
        click.echo(click.style("\nSecurity audit: clean", bold=True, fg="green"))


@click.group()
@click.version_option()
def main() -> None:
    """aether-arch: requirements -> validated architecture -> draw.io."""


@main.command()
@click.argument("requirement", nargs=-1, required=True)
@click.option("-o", "--output", "output_path", type=click.Path(path_type=Path), default=None,
              help="Output .drawio path. Default: <slug>.drawio in cwd.")
@click.option("--json-out", "json_path", type=click.Path(path_type=Path), default=None,
              help="Optional path for the JSON architecture sidecar.")
@click.option("--no-report", is_flag=True, help="Suppress the human-readable summary.")
def build(
    requirement: tuple[str, ...],
    output_path: Path | None,
    json_path: Path | None,
    no_report: bool,
) -> None:
    """Synthesise an architecture from a free-text REQUIREMENT."""
    req = " ".join(requirement).strip()
    if not req:
        raise click.UsageError("requirement is empty")

    architect = LeadArchitect()
    result = architect.synthesise(req)

    if output_path is None:
        slug = "".join(c if c.isalnum() else "-" for c in result.architecture.title.lower()).strip("-")
        output_path = Path(f"{slug or 'architecture'}.drawio")

    xml = emit_drawio(result.architecture, result.plan)
    output_path.write_text(xml, encoding="utf-8")

    sidecar = json_path or output_path.with_suffix(".json")
    sidecar.write_text(
        json.dumps(result.architecture.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    # Block deploy if any errors remain. Mirrors PDF HITL stance.
    has_errors = any(f.severity == "error" for f in result.trace.findings)

    if not no_report:
        _print_report(result)
        click.echo(f"\nWrote {output_path}")
        click.echo(f"Wrote {sidecar}")

    if has_errors:
        click.echo(click.style("\nDesign has unresolved security errors - requires human review.", fg="red"))
        sys.exit(2)


@main.command("explain")
@click.argument("paper_id")
def explain(paper_id: str) -> None:
    """Print the canonical paper entry for PAPER_ID."""
    from aether.knowledge.papers import PAPERS
    if paper_id not in PAPERS:
        raise click.ClickException(f"unknown paper id: {paper_id}")
    p = PAPERS[paper_id]
    click.echo(click.style(p.title, bold=True))
    click.echo(f"  authors:      {p.authors}")
    click.echo(f"  topics:       {', '.join(p.topics)}")
    click.echo(f"  contribution: {p.contribution}")


@main.command("papers")
@click.option("--topic", default=None, help="Filter by topic tag.")
def papers_cmd(topic: str | None) -> None:
    """List the 40 canonical papers in the knowledge base."""
    from aether.knowledge.papers import PAPERS, by_topic
    selected = list(PAPERS.values()) if topic is None else by_topic(topic)
    for p in selected:
        click.echo(f"  {p.id:24s}  {p.title}")
    click.echo(f"\n{len(selected)} papers.")


if __name__ == "__main__":  # pragma: no cover
    main()
