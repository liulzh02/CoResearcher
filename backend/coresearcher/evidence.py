from __future__ import annotations

from coresearcher.domain.state import (
    Claim,
    CritiqueNote,
    EvidenceItem,
    ExtractionStatus,
    PaperRecord,
    SourceLocator,
    SourceType,
)


def normalize_paper(
    *,
    title: str,
    authors: list[str] | None = None,
    locator: SourceLocator,
    venue_or_source: str | None = None,
    year: int | None = None,
    extraction_status: ExtractionStatus = ExtractionStatus.PENDING,
    quality_signals: dict | None = None,
) -> PaperRecord:
    return PaperRecord(
        title=title,
        authors=authors or [],
        venue_or_source=venue_or_source or locator.title,
        year=year,
        locator=locator,
        extraction_status=extraction_status,
        quality_signals=quality_signals or {},
    )


def make_url_locator(url: str, title: str | None = None) -> SourceLocator:
    return SourceLocator(type=SourceType.URL, path_or_url=url, title=title)


def create_evidence(
    summary: str,
    *,
    source_locator: SourceLocator | None = None,
    paper_id: str | None = None,
    quote: str | None = None,
    quality_signals: dict | None = None,
    user_provided_assumption: bool = False,
) -> EvidenceItem:
    return EvidenceItem(
        summary=summary,
        source_locator=source_locator,
        paper_id=paper_id,
        quote=quote,
        quality_signals=quality_signals or {},
        user_provided_assumption=user_provided_assumption,
    )


def create_claim(
    text: str,
    *,
    evidence_ids: list[str] | None = None,
    critique_note_ids: list[str] | None = None,
    user_provided_assumption: bool = False,
) -> Claim:
    return Claim(
        text=text,
        evidence_ids=evidence_ids or [],
        critique_note_ids=critique_note_ids or [],
        user_provided_assumption=user_provided_assumption,
    )


def create_critique(
    text: str,
    *,
    challenged_claim_ids: list[str] | None = None,
    challenged_evidence_ids: list[str] | None = None,
    severity: str = "medium",
) -> CritiqueNote:
    return CritiqueNote(
        text=text,
        challenged_claim_ids=challenged_claim_ids or [],
        challenged_evidence_ids=challenged_evidence_ids or [],
        severity=severity,
    )

