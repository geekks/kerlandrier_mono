import importlib
import os
from pathlib import Path
from urllib.parse import urlparse

import pytest
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=False)


def pytest_addoption(parser):
    parser.addoption("--live-front", action="store_true", help="Run browser checks against a running front")
    parser.addoption("--live-mistral", action="store_true", help="Send the test poster to Mistral")
    parser.addoption("--live-openagenda", action="store_true", help="Create and delete an event on the test agenda")


def pytest_collection_modifyitems(config, items):
    for item in items:
        for marker in ("front", "mistral", "openagenda"):
            if marker in item.keywords and not config.getoption(f"--live-{marker}"):
                item.add_marker(pytest.mark.skip(reason=f"Requires --live-{marker}"))


def required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.fail(f"Set {name} before running this test", pytrace=False)
    return value


@pytest.fixture(scope="session")
def front_config():
    front_url = required_env("KL_TEST_FRONT_URL").rstrip("/")
    response = requests.get(f"{front_url}/config.json", timeout=15)
    response.raise_for_status()
    config = response.json()
    api_url = config["API_URL"].rstrip("/")
    parsed = urlparse(api_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        pytest.fail("config.json must contain an absolute HTTP(S) API_URL")
    return front_url, api_url, str(config["OA_UID"])


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def api_module(tmp_path_factory):
    # Prevent API imports from using a real database or credentials from .env.
    values = {
        "DB_PATH": str(tmp_path_factory.mktemp("api") / "auth.db"),
        "JWT_SECRET": "test-only-secret-at-least-32-bytes-long",
        "SENDER_EMAIL": "test@example.org",
        "SENDER_EMAIL_PASSWORD": "test-only",
        "RECEIVER_EMAIL": "test@example.org",
        "OA_PUBLIC_KEY": "test-only",
        "OA_SECRET_KEY": "test-only",
        "ICS_PRIVATE_URL_KLR_FB": "https://example.org/test",
        "MISTRAL_PRIVATE_API_KEY": "test-only",
        "IMGBB_PRIVATE_API_KEY": "test-only",
    }
    original = {key: os.environ.get(key) for key in values}
    try:
        os.environ.update(values)
        module = importlib.import_module("main")
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    yield module
    module.db.close()


@pytest.fixture
def api_client(api_module):
    from fastapi.testclient import TestClient

    with TestClient(api_module.app) as client:
        yield client
    api_module.app.dependency_overrides.clear()
