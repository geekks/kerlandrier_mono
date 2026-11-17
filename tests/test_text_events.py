import json
from types import SimpleNamespace

import pytest

import text_events
from script.libs import getOaLocation


@pytest.mark.parametrize(
    "date, expected_offset",
    [("2026-07-12", "+02:00"), ("2026-12-12", "+01:00")],
)
def test_gemini_events_keep_local_time_and_use_default_location(monkeypatch, date, expected_offset):
    response = {
        "events": [{
            "title": "Concert",
            "description": "Musique",
            "timings": [{
                "begin": f"{date}T18:00:00",
                "end": f"{date}T20:00:00",
            }],
            "locationUid": None,
        }],
    }
    models = SimpleNamespace(generate_content=lambda **kwargs: SimpleNamespace(text=json.dumps(response)))
    monkeypatch.setattr(text_events.genai, "Client", lambda api_key: SimpleNamespace(models=models))

    events = text_events.process_event_descriptions(["Concert à 18h"], [], "test-key", default_location_uid=42)

    assert events[0]["locationUid"] == 42
    assert events[0]["timings"] == [{
        "begin": f"{date}T18:00:00{expected_offset}",
        "end": f"{date}T20:00:00{expected_offset}",
    }]


def test_existing_openagenda_location_is_matched_without_creation(monkeypatch):
    locations = [{"uid": 42, "name": "Espace Benoîte Groult", "address": "Rue du Coat-Kaër, Quimperlé"}]
    monkeypatch.setattr(getOaLocation, "get_locations", lambda *args: locations)

    def forbid_creation(*args, **kwargs):
        pytest.fail("An existing location must not be created again")

    monkeypatch.setattr(getOaLocation, "post_location", forbid_creation)
    uid = getOaLocation.get_or_create_oa_location(
        "Espace Benoîte Groult", access_token="test-token",
        public_key="test-key", locations_api_url="https://example.test/locations",
    )
    assert uid == 42
