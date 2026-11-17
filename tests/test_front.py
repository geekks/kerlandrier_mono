import hashlib
from pathlib import Path
from urllib.parse import urlparse

import pytest

from conftest import required_env

pytestmark = pytest.mark.front
POSTER = Path(__file__).resolve().parents[1] / "api/tests/event_test_festnoz.jpg"


def test_home_displays_events_from_openagenda(page, front_config):
    front_url, _, agenda_uid = front_config
    responses = []
    events_path = f"/v2/agendas/{agenda_uid}/events"
    page.on(
        "response",
        lambda response: responses.append(response)
        if urlparse(response.url).hostname == "api.openagenda.com"
        and urlparse(response.url).path == events_path
        else None,
    )
    page.goto(front_url, wait_until="domcontentloaded")
    page.locator(".evenement").first.wait_for(state="visible", timeout=30000)
    assert responses, "No OpenAgenda event request was made"
    assert responses[-1].status == 200
    assert len(responses[-1].json()["events"]) > 0
    assert page.locator(".evenement").count() > 0


def test_login_through_front(page, front_config):
    front_url, api_url, _ = front_config
    username = required_env("KL_TEST_USERNAME")
    password = required_env("KL_TEST_PASSWORD")
    page.goto(f"{front_url}/input", wait_until="networkidle")
    page.get_by_placeholder("Nom d'utilisateur").fill(username)
    page.get_by_placeholder("Mot de passe").fill(password)
    with page.expect_response(
        lambda response: response.url == f"{api_url}/auth"
        and response.request.method == "POST",
        timeout=30000,
    ) as auth_response:
        page.get_by_role("button", name="Connexion").click()
    assert auth_response.value.status == 200
    assert auth_response.value.json()["success"]
    page.get_by_role("button", name="Se déconnecter").wait_for(timeout=10000)
    assert page.evaluate("Boolean(localStorage.getItem('kl_token'))")


def test_image_upload_ui_without_publication(page, front_config):
    front_url, api_url, _ = front_config
    assert POSTER.is_file(), f"Missing poster: {POSTER}"
    uploads = []

    def intercept_upload(route):
        uploads.append((route.request.url, route.request.post_data_buffer))
        route.fulfill(
            status=200,
            json={
                "success": True,
                "event": {
                    "name": "Fest-noz",
                    "location": "Espace Benoîte Groult",
                    "description": "Réponse simulée",
                    "start": "2026-12-12T18:00:00+01:00",
                    "end": "2026-12-13T01:00:00+01:00",
                    "url": "https://example.org/test",
                },
            },
        )

    page.route("**/image/upload", intercept_upload)
    page.add_init_script("""
        localStorage.setItem('kl_token', 'test-token');
        const originalFetch = window.fetch;
        window.fetch = async (url, options) => {
            if (String(url).endsWith('/image/upload')) {
                const file = options.body.get('file');
                const digest = await crypto.subtle.digest('SHA-256', await file.arrayBuffer());
                window.testUploadHash = Array.from(new Uint8Array(digest))
                    .map(byte => byte.toString(16).padStart(2, '0')).join('');
            }
            return originalFetch(url, options);
        };
    """)
    page.goto(f"{front_url}/upload", wait_until="networkidle")
    page.locator("#fileInput").set_input_files(str(POSTER))
    page.get_by_role("button", name="Envoyer").click()
    page.get_by_text("Fest-noz", exact=True).wait_for(timeout=10000)
    assert page.get_by_text("Espace Benoîte Groult", exact=True).is_visible()
    assert len(uploads) == 1
    assert uploads[0][0] == f"{api_url}/image/upload"
    assert f'filename="{POSTER.name}"'.encode() in uploads[0][1]
    assert page.evaluate("window.testUploadHash") == hashlib.sha256(POSTER.read_bytes()).hexdigest()
