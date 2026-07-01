import pytest
from fastapi.testclient import TestClient

from coresearcher.gateway.app import create_app
from coresearcher.services import ResearchService


async def test_research_service_run_and_events():
    service = ResearchService()
    thread = await service.create_thread(user_id="u1", initial_message="Study LLM research agents")
    updated, events = await service.run_research(
        thread_id=thread.id,
        user_id="u1",
        message="Please review literature and identify limitations.",
    )
    assert updated.messages[-1].role == "assistant"
    assert any(event.type.value == "subagent.completed" for event in events)
    assert updated.state.artifacts


def test_create_app_has_health_route():
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/research/threads" in paths
    assert "/research/threads/{thread_id}/runs" in paths
    assert "/research/threads/{thread_id}/messages" in paths


def test_api_thread_run_sse_artifact_and_events():
    client = TestClient(create_app())
    assert client.get("/health").json()["status"] == "ok"

    created = client.post(
        "/research/threads",
        json={"initial_message": "Study LLM research agents"},
        headers={"x-user-id": "u1"},
    )
    assert created.status_code == 200
    thread_id = created.json()["thread"]["id"]

    run = client.post(
        f"/research/threads/{thread_id}/runs",
        json={"message": "Please review literature and identify limitations."},
        headers={"x-user-id": "u1"},
    )
    assert run.status_code == 200
    payload = run.json()
    assert payload["run_id"]
    assert payload["final_response"]
    assert payload["thread"]["state"]["artifacts"]

    messages = client.get(
        f"/research/threads/{thread_id}/messages",
        headers={"x-user-id": "u1"},
    )
    assert messages.status_code == 200
    assert messages.json()["messages"][-1]["role"] == "assistant"

    artifact_id = payload["thread"]["state"]["artifacts"][0]["id"]
    artifact = client.get(
        f"/research/threads/{thread_id}/artifacts/{artifact_id}",
        headers={"x-user-id": "u1"},
    )
    assert artifact.status_code == 200
    assert "Research Brief" in artifact.json()["content"]

    events = client.get(f"/research/runs/{payload['run_id']}/events")
    assert events.status_code == 200
    assert any(event["type"] == "subagent.completed" for event in events.json()["events"])

    stream = client.post(
        f"/research/threads/{thread_id}/runs/stream",
        json={"message": "Need a direct next step."},
        headers={"x-user-id": "u1"},
    )
    assert stream.status_code == 200
    assert "event: run.started" in stream.text


def test_api_scopes_threads_by_user_and_structures_errors():
    client = TestClient(create_app())
    created = client.post(
        "/research/threads",
        json={"initial_message": "Private thread"},
        headers={"x-user-id": "u1"},
    )
    thread_id = created.json()["thread"]["id"]
    hidden = client.get(f"/research/threads/{thread_id}", headers={"x-user-id": "u2"})
    assert hidden.status_code == 404

    stream = client.post(
        "/research/threads/missing/runs/stream",
        json={"message": "Trigger missing thread"},
        headers={"x-user-id": "u1"},
    )
    assert stream.status_code == 200
    assert "error.structured" in stream.text
