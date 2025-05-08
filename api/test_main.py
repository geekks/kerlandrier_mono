import os,sys
import pytest
import requests, logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from db import create_user, initialize_database, DB_Connection
from script.libs.HttpRequests import get_event
from api_utils import get_event_keywords, patch_event
from tests.test_event import OaEvent
from script.configuration import config

OaTestEventUID=20368810
db_path_test = "db_tests/auth.db"
api_url = config.OA_API_URL
oa_public_key = config.OA_PUBLIC_KEY

# Initialize the database and create a test user
@pytest.fixture(scope="module", autouse=True)
def setup():
    if os.path.exists(db_path_test):
        os.remove(db_path_test)
    initialize_database(db_path_test)
    db = DB_Connection(db_path_test)
    create_user(db_path_test, 'testuser', 'testpassword')

# Start the FastAPI server and mock data server
@pytest.fixture(scope="module")
def start_servers():
    import subprocess
    import time

 # Set the environment variable for the subprocess
    env = os.environ.copy()
    env["DB_PATH"] = db_path_test
    # Start FastAPI server
    try:
        fastapi_process = subprocess.Popen(
            ["uvicorn", "main:app", "--port", "8000"],
            env=env
        )
        #fastapi_process = subprocess.Popen(
    except Exception as e:
        logging.error(f"Failed to start FastAPI server: {e}")
        raise
    # Wait for servers to start
    time.sleep(10)

    yield

    # Terminate servers
    fastapi_process.terminate()

def test_ping_api(start_servers):
    response = requests.get("http://127.0.0.1:8000", timeout=10)
    assert response.status_code == 404
    assert response.json()["message"] == "RTFM"


def test_authentication(setup,start_servers):
    response = requests.post("http://localhost:8000/auth", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "access_token" in response.json()

def test_oatoken(setup,start_servers):
    response = requests.post("http://localhost:8000/auth", json={"username": "testuser", "password": "testpassword"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/auth/oatoken", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_update_event_keywords(setup,start_servers):
    # Step 1: Authenticate and get the token
    response = requests.post("http://localhost:8000/auth", json={"username": "testuser", "password": "testpassword"})
    access_token = response.json()["access_token"]

    # Step 2: Fetch the test event from OpenAgenda
    event_uid = 20368810
    fetched_event = get_event(oa_public_key, event_uid)

    # Step 3: Compare the fetched event with the OaEvent in test_event.py
    fetched_event.get('event').pop("updatedAt")
    assert fetched_event == OaEvent, "Fetched event does not match the expected event"

    # Step 4: Request keywords for the event and compare the keywords with the ones existing in OaEvent
    
    keywords = get_event_keywords(event_uid, api_url, oa_public_key)
    expected_keywords = OaEvent['event']['keywords']['fr']
    assert keywords == expected_keywords, f"Keywords do not match. Expected: {expected_keywords}, but got: {keywords}"
    
    # Step 5: Apply a patch to the event with new keywords
    new_keywords = ["new", "keywords"]
    patch_response = patch_event(access_token, event_uid, new_keywords, api_url)
    assert patch_response["success"] == True, "Failed to patch event keywords"
    assert patch_response["event"]["keywords"]["fr"] == new_keywords, "Patched keywords do not match the expected keywords"

    # Step 6: Request the updated keywords and compare them
    updated_keywords = get_event_keywords(event_uid, api_url, oa_public_key)
    assert updated_keywords == new_keywords, "Updated keywords do not match the expected keywords"