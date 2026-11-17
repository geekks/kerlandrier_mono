import os
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
import requests

from conftest import required_env


@pytest.mark.openagenda
def test_create_and_delete_event_on_test_agenda(api_client, api_module, monkeypatch, request):
    from script.libs.HttpRequests import get_nonce

    agenda_uid = required_env("KL_TEST_OA_AGENDA_UID")
    if agenda_uid != "5364789":
        pytest.fail("Only the designated test agenda 5364789 may be used")
    if os.environ.get("KL_TEST_OA_ALLOW_WRITE") != "1":
        pytest.fail("Set KL_TEST_OA_ALLOW_WRITE=1 to create a test event")
    location_uid = int(required_env("KL_TEST_OA_LOCATION_UID"))
    secret = required_env("KL_TEST_OA_SECRET_KEY")
    token_response = requests.post(
        "https://api.openagenda.com/v2/requestAccessToken",
        json={"grant_type": "client_credentials", "code": secret},
        timeout=30,
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    events_url = f"https://api.openagenda.com/v2/agendas/{agenda_uid}/events"
    monkeypatch.setattr(api_module.config, "AGENDA_UID", agenda_uid)
    monkeypatch.setattr(api_module.oa, "getToken", lambda: access_token)
    api_module.app.dependency_overrides[api_module.get_current_user] = lambda: {"user_id": 1}
    title = f"TEST AUTOMATIQUE - {uuid.uuid4().hex}"
    start = datetime.now(ZoneInfo("Europe/Paris")) + timedelta(days=30)
    response = api_client.post("/text/payload", json={"events": [{
        "title": title,
        "description": "Événement de test à supprimer",
        "locationUid": location_uid,
        "timings": [{"begin": start.isoformat(), "end": (start + timedelta(hours=1)).isoformat()}],
    }]})
    response.raise_for_status()
    result = response.json()["results"][0]
    openagenda_response = result.get("openAgendaResponse") or {}
    body = openagenda_response.get("body")
    created_event = body.get("event", {}) if isinstance(body, dict) else {}
    uid = result.get("uid") or created_event.get("uid")

    if uid:
        def cleanup():
            deletion = requests.delete(
                f"{events_url}/{uid}",
                headers={"access-token": access_token, "nonce": get_nonce()},
                timeout=30,
            )
            assert deletion.ok, f"Could not delete test event {uid}: HTTP {deletion.status_code}"
            assert str(deletion.json().get("event", {}).get("uid")) == str(uid)

        request.addfinalizer(cleanup)

    assert result["success"], f"Creation failed for {title}: {result}"
    assert uid, f"Creation returned no UID; search for {title} on agenda {agenda_uid}"
    assert response.json()["created"] == 1
    assert created_event["title"]["fr"] == title
