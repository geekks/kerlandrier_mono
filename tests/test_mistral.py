import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pytest

from conftest import required_env


@pytest.fixture(scope="session")
def poster_event():
    from script.mistral_images import getMistralImageEvent

    image = Path(__file__).resolve().parents[1] / "api/tests/event_test_festnoz.jpg"
    assert image.is_file(), f"Missing poster: {image}"
    return getMistralImageEvent(required_env("MISTRAL_PRIVATE_API_KEY"), image_path=str(image))


@pytest.mark.mistral
def test_poster_extraction_without_openagenda_publication(poster_event):
    event = poster_event
    start = datetime.fromisoformat(event.date_debut.replace("Z", "+00:00"))
    assert (start.month, start.day, start.hour, start.minute) == (12, 12, 18, 0), (
        f"date_debut={event.date_debut!r}, heure_debut={event.heure_debut!r}"
    )
    assert event.heure_debut == "18:00"
    location = unicodedata.normalize("NFKD", event.lieu.lower())
    location = re.sub(r"[^a-z]", "", location)
    assert "benoitegroult" in location, f"Unexpected venue: {event.lieu!r}"


@pytest.fixture
def location_settings():
    agenda_uid = required_env("KL_TEST_OA_AGENDA_UID")
    if agenda_uid != "5364789":
        pytest.fail("Only the designated test agenda 5364789 may be used")
    return (
        agenda_uid,
        required_env("KL_TEST_OA_LOCATION_UID"),
        required_env("KL_TEST_OA_PUBLIC_KEY"),
    )


@pytest.mark.mistral
@pytest.mark.openagenda
def test_poster_location_matches_openagenda(location_settings, poster_event, monkeypatch):
    from script.libs import getOaLocation

    agenda_uid, expected_uid, public_key = location_settings

    def forbid_location_creation(*args, **kwargs):
        pytest.fail(f"No matching OpenAgenda location for {poster_event.lieu!r}; creation forbidden")

    monkeypatch.setattr(getOaLocation, "post_location", forbid_location_creation)
    uid = getOaLocation.get_or_create_oa_location(
        searched_location=poster_event.lieu,
        access_token="",
        public_key=public_key,
        locations_api_url=f"https://api.openagenda.com/v2/agendas/{agenda_uid}/locations",
    )
    assert str(uid) == expected_uid, f"Location {poster_event.lieu!r} matched UID {uid}, expected {expected_uid}"
