from types import SimpleNamespace

import bcrypt
import pytest
from pydantic import SecretStr


@pytest.fixture
def authenticated_client(api_client, api_module):
    api_module.app.dependency_overrides[api_module.get_current_user] = lambda: {"user_id": 1}
    return api_client


def test_authentication_issues_usable_token_and_rejects_bad_credentials(api_client, api_module, monkeypatch):
    password_hash = bcrypt.hashpw(b"correct-password", bcrypt.gensalt()).decode()
    monkeypatch.setattr(
        api_module.api_utils,
        "get_user_by_username",
        lambda db, username: (7, password_hash) if username == "alice" else None,
    )
    for username, password in [("alice", "wrong"), ("unknown", "correct-password")]:
        response = api_client.post("/auth", json={"username": username, "password": password})
        assert response.status_code == 401

    response = api_client.post("/auth", json={"username": "alice", "password": "correct-password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    response = api_client.post(
        "/text/payload", json={"events": []}, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "No events provided"


@pytest.mark.parametrize("authorization", ["Basic token", "Bearer invalid"])
def test_protected_endpoint_rejects_invalid_authentication(api_client, authorization):
    response = api_client.post(
        "/text/payload", json={"events": []}, headers={"Authorization": authorization}
    )
    assert response.status_code == 401


def test_text_payload_requires_authentication(api_client):
    response = api_client.post("/text/payload", json={"events": []})
    assert response.status_code == 401


def test_text_payload_creates_event(api_client, api_module, monkeypatch):
    api_module.app.dependency_overrides[api_module.get_current_user] = lambda: {"user_id": 1}
    monkeypatch.setattr(api_module.oa, "getToken", lambda: "test-token")
    calls = []

    def create_event(token, event, events_api_url):
        calls.append((token, event, events_api_url))
        return {"status_code": 200, "body": {"event": {"uid": 123, "slug": "test-event"}}}

    monkeypatch.setattr(api_module, "create_event_with_response", create_event)
    response = api_client.post("/text/payload", json={"events": [{
        "title": "Test",
        "description": "Description",
        "locationUid": 42,
        "timings": [{"begin": "2026-12-05T20:30:00+01:00", "end": "2026-12-05T22:30:00+01:00"}],
    }]})

    assert response.status_code == 200
    assert response.json()["created"] == 1
    assert response.json()["results"][0]["uid"] == 123
    assert len(calls) == 1
    assert calls[0][1]["title"] == {"fr": "Test"}
    assert calls[0][1]["locationUid"] == 42


def test_text_payload_reports_partial_failure(authenticated_client, api_module, monkeypatch):
    monkeypatch.setattr(api_module.oa, "getToken", lambda: "test-token")
    responses = iter([
        {"status_code": 200, "body": {"event": {"uid": 123, "slug": "event"}}},
        {"status_code": 400, "body": {"message": "invalid location"}},
    ])
    monkeypatch.setattr(api_module, "create_event_with_response", lambda *args, **kwargs: next(responses))
    payload = {"description": "Description", "timings": [], "locationUid": 42}
    response = authenticated_client.post("/text/payload", json={"events": [
        {**payload, "title": "Premier"},
        {**payload, "title": "Second"},
    ]})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["created"] == 1
    assert body["results"][0]["uid"] == 123
    assert body["results"][1]["success"] is False
    assert body["results"][1]["openAgendaResponse"]["body"]["message"] == "invalid location"


def test_text_inputs_splits_events_and_passes_locations(authenticated_client, api_module, monkeypatch):
    monkeypatch.setattr(api_module.config, "GEMINI_API_KEY", SecretStr("test-key"))
    monkeypatch.setattr(api_module.oa, "getToken", lambda: "test-token")
    locations = [{"uid": 42, "name": "Salle"}]
    monkeypatch.setattr(api_module.text_events, "fetch_agenda_locations", lambda token, url: locations)
    calls = []

    def process(descriptions, found_locations, **kwargs):
        calls.append((descriptions, found_locations, kwargs))
        return [{"title": "Premier"}, {"title": "Second"}]

    monkeypatch.setattr(api_module.text_events, "process_event_descriptions", process)
    response = authenticated_client.post("/text/inputs", json={"text": " Premier \n---\n --- \nSecond "})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert calls[0][0] == ["Premier", "Second"]
    assert calls[0][1] == locations
    assert calls[0][2]["gemini_api_key"] == "test-key"


def test_text_inputs_rejects_empty_text_and_missing_key(authenticated_client, api_module, monkeypatch):
    response = authenticated_client.post("/text/inputs", json={"text": " --- "})
    assert response.status_code == 400
    monkeypatch.setattr(api_module.config, "GEMINI_API_KEY", None)
    response = authenticated_client.post("/text/inputs", json={"text": "Concert"})
    assert response.status_code == 500
    assert response.json()["detail"] == "GEMINI_API_KEY is not configured"


@pytest.mark.parametrize("existing, expected_calls", [(["concert"], 0), (["old"], 1)])
def test_keywords_only_patch_when_changed(authenticated_client, api_module, monkeypatch, existing, expected_calls):
    monkeypatch.setattr(api_module.oa, "getToken", lambda: "test-token")
    monkeypatch.setattr(api_module.api_utils, "get_event_keywords", lambda *args, **kwargs: existing)
    calls = []
    monkeypatch.setattr(
        api_module, "patch_event",
        lambda token, uid, body: calls.append((token, uid, body)) or {"uid": uid},
    )
    response = authenticated_client.patch("/event/keywords", json={"uid": 123, "keywords": ["concert"]})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(calls) == expected_calls
    if calls:
        assert calls[0][2] == {"data": {"keywords": {"fr": ["concert"]}}}


def test_upload_runs_pipeline_and_removes_file(authenticated_client, api_module, monkeypatch, tmp_path):
    image = tmp_path / "poster.jpg"

    def save_image(file):
        image.write_bytes(file.file.read())
        return str(image)

    monkeypatch.setattr(api_module.api_utils, "saveImagePost", save_image)
    calls = []

    def upload_image(**kwargs):
        assert image.read_bytes() == b"test-image"
        return "https://example.test/poster.jpg"

    monkeypatch.setattr(api_module, "postImageToImgbb", upload_image)
    monkeypatch.setattr(api_module.api_utils, "send_url_to_mistral", lambda **kwargs: "extracted-event")
    monkeypatch.setattr(api_module.oa, "getToken", lambda: "test-token")
    event = SimpleNamespace(title=SimpleNamespace(fr="Fest-noz"), location=SimpleNamespace(name="Salle"))

    def create_event(extracted, **kwargs):
        calls.append((extracted, kwargs))
        return event

    monkeypatch.setattr(api_module, "postMistralEventToOa", create_event)
    monkeypatch.setattr(api_module.api_utils, "excerptOAEvent", lambda event: {
        "success": True, "event": {"name": event.title.fr},
    })
    response = authenticated_client.post(
        "/image/upload", files={"file": ("poster.jpg", b"test-image", "image/jpeg")}
    )
    assert response.status_code == 200
    assert response.json()["event"]["name"] == "Fest-noz"
    assert calls[0][0] == "extracted-event"
    assert calls[0][1]["image_url"] == "https://example.test/poster.jpg"
    assert not image.exists()
