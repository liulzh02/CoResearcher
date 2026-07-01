from __future__ import annotations

from coresearcher.domain.state import ArtifactRecord, ArtifactType, ResearchState


def _claim_line(state: ResearchState, claim_id: str) -> str:
    claim = next((item for item in state.claims if item.id == claim_id), None)
    if not claim:
        return f"- Missing claim reference: {claim_id}"
    refs = ", ".join(claim.evidence_ids or claim.critique_note_ids) or "unsupported"
    label = "assumption" if claim.user_provided_assumption else claim.status.value
    return f"- [{claim.id}] {claim.text} ({label}; refs: {refs})"


def create_research_brief(state: ResearchState, title: str = "Research Brief") -> ArtifactRecord:
    lines = [
        f"# {title}",
        "",
        "## Research Question",
        state.question.text or "Not yet specified.",
        "",
        "## Claims",
    ]
    lines.extend(_claim_line(state, claim.id) for claim in state.claims)
    if not state.claims:
        lines.append("- No durable claims yet.")
    lines.extend(
        [
            "",
            "## Evidence",
            *[
                f"- [{item.id}] {item.summary} (source: "
                f"{item.source_locator.path_or_url if item.source_locator else 'user assumption'})"
                for item in state.evidence_items
            ],
            "",
            "## Open Questions",
            *[f"- [{item.id}] {item.text}" for item in state.open_questions],
            "",
            "## Critique",
            *[f"- [{item.id}] {item.text}" for item in state.critique_notes],
        ]
    )
    content = "\n".join(lines)
    return ArtifactRecord(
        type=ArtifactType.RESEARCH_BRIEF,
        title=title,
        content=content,
        claim_ids=[claim.id for claim in state.claims],
        evidence_ids=[item.id for item in state.evidence_items],
        critique_note_ids=[item.id for item in state.critique_notes],
    )


def create_reading_note(state: ResearchState, paper_id: str) -> ArtifactRecord:
    paper = next((item for item in state.papers if item.id == paper_id), None)
    if not paper:
        raise ValueError(f"Unknown paper: {paper_id}")
    evidence = [item for item in state.evidence_items if item.paper_id == paper_id]
    content = "\n".join(
        [
            f"# Reading Note: {paper.title}",
            "",
            f"- Authors: {', '.join(paper.authors) or 'Unknown'}",
            f"- Source: {paper.locator.path_or_url or paper.locator.title or paper.id}",
            f"- Extraction status: {paper.extraction_status.value}",
            "",
            "## Evidence Notes",
            *[f"- [{item.id}] {item.summary}" for item in evidence],
        ]
    )
    return ArtifactRecord(
        type=ArtifactType.READING_NOTE,
        title=f"Reading Note: {paper.title}",
        content=content,
        evidence_ids=[item.id for item in evidence],
        source_locators=[paper.locator],
    )


def create_evidence_map(state: ResearchState) -> ArtifactRecord:
    rows = ["# Evidence Map", "", "| Claim | Evidence | Status |", "| --- | --- | --- |"]
    for claim in state.claims:
        refs = ", ".join(claim.evidence_ids) or "unsupported"
        rows.append(f"| {claim.id}: {claim.text} | {refs} | {claim.status.value} |")
    return ArtifactRecord(
        type=ArtifactType.EVIDENCE_MAP,
        title="Evidence Map",
        content="\n".join(rows),
        claim_ids=[claim.id for claim in state.claims],
        evidence_ids=[item.id for item in state.evidence_items],
    )

