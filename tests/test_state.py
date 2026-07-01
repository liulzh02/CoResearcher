import pytest
from pydantic import ValidationError

from coresearcher.artifacts import create_research_brief
from coresearcher.domain.state import Claim, Decision, EvidenceItem, ResearchState
from coresearcher.evidence import create_claim, create_evidence, make_url_locator
from coresearcher.storage import InMemoryResearchRepository
from coresearcher.domain.state import ResearchThread


def test_evidence_requires_source_or_assumption():
    with pytest.raises(ValidationError):
        EvidenceItem(summary="No source")


def test_claim_requires_evidence_critique_or_assumption():
    with pytest.raises(ValidationError):
        Claim(text="Unsupported durable claim")


async def test_state_persistence_and_decision_recording():
    repo = InMemoryResearchRepository()
    thread = ResearchThread(user_id="u1")
    evidence = create_evidence(
        "Tool use improves traceability.",
        source_locator=make_url_locator("https://example.test/paper", "Paper"),
    )
    claim = create_claim("Traceability needs structured evidence.", evidence_ids=[evidence.id])
    thread.state.evidence_items.append(evidence)
    thread.state.claims.append(claim)
    thread.state.decisions.append(
        Decision(text="Focus on traceable evidence.", rationale="It reduces unsupported claims.")
    )
    await repo.create(thread)
    loaded = await repo.get(thread.id, user_id="u1")
    assert loaded is not None
    assert loaded.state.claims[0].evidence_ids == [evidence.id]
    assert loaded.state.decisions[0].rationale


def test_artifact_links_back_to_state():
    state = ResearchState()
    evidence = create_evidence("Evidence", source_locator=make_url_locator("https://example.test"))
    claim = create_claim("Claim", evidence_ids=[evidence.id])
    state.evidence_items.append(evidence)
    state.claims.append(claim)
    artifact = create_research_brief(state)
    assert claim.id in artifact.claim_ids
    assert evidence.id in artifact.evidence_ids
    assert f"[{claim.id}]" in artifact.content

