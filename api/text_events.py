import json
import logging
from typing import List, Optional

import requests
from google import genai
from pydantic import BaseModel, Field

from script.libs.utils import naive_str_to_paris_iso

GEMINI_MODEL = "gemini-2.5-flash"


class OpenAgendaEventPayload(BaseModel):
    title: str = Field(..., description="Event title (string)")
    summary: Optional[str] = Field(None, description="Short summary/catchphrase (string)")
    description: str = Field(..., max_length=49, description="Short description (maximum 49 characters)")
    longDescription: Optional[str] = Field(None, description="Detailed description (string)")
    keywords: Optional[dict] = Field(None, description="Keywords object, e.g., {'fr': ['tag1', 'tag2']}")
    registration: Optional[List[dict]] = Field(None, description="Registration links, e.g., [{'type': 'link', 'value': 'https://...'}]")
    timings: List[dict] = Field(..., description="List of timings with 'begin' and 'end' in ISO 8601 format")
    locationUid: Optional[int] = Field(None, description="The matched OpenAgenda location UID, or null if not found")


class BatchEventOutput(BaseModel):
    events: List[OpenAgendaEventPayload]


def split_raw_events(text: str) -> List[str]:
    """Splits a text into event descriptions separated by '---'."""
    return [block.strip() for block in text.split("---") if block.strip()]


def fetch_agenda_locations(access_token: str, oa_api_url: str) -> List[dict]:
    """Fetches all the agenda locations (paginated), keeping only the useful fields."""
    url = f"{oa_api_url}/locations"
    headers = {"access-token": access_token}
    locations: List[dict] = []
    after_cursor = None

    while True:
        params = {"size": 100}
        if after_cursor:
            if isinstance(after_cursor, list):
                for i, val in enumerate(after_cursor):
                    params[f"after[{i}]"] = val
            else:
                params["after"] = after_cursor

        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            logging.warning(f"Failed to fetch locations page (Status {response.status_code}): {response.text}")
            break

        data = response.json()
        page = data.get("locations", [])
        if not page:
            break
        locations.extend(
            {"uid": loc.get("uid"), "name": loc.get("name"), "address": loc.get("address"), "city": loc.get("city")}
            for loc in page
        )
        after_cursor = data.get("after")
        if not after_cursor:
            break

    return locations


def process_event_descriptions(descriptions: List[str],
                               locations: List[dict],
                               gemini_api_key: str,
                               default_location_uid: Optional[int] = None) -> List[dict]:
    """Converts raw text descriptions into OpenAgenda payloads using Gemini."""
    client = genai.Client(api_key=gemini_api_key)
    prompt = f"""
    You are an expert event data ingestion agent for OpenAgenda. 
    Convert the following list of raw event descriptions into structured JSON payloads conforming to OpenAgenda API v2 standards.
    Current Year context: 2026. Handle relative dates correctly. All times are local Paris times: output the naive local time exactly as given in the text, WITHOUT any timezone, offset or "Z" (format YYYY-MM-DDTHH:MM:SS). Do not convert anything; the offset is applied afterwards.
    
    Here is the official list of registered locations available in the OpenAgenda database for this agenda:
    {json.dumps(locations, ensure_ascii=False, indent=2)}

    For each event description:
    1. Identify the venue/location, match it to the most appropriate location from the official list above, and extract its integer 'uid' into the 'locationUid' field. If no matching location can be determined, set 'locationUid' to null.
    2. Generate 2 or 3 short, funny keywords about the event in French Keywords object with 2-3 short. They should stand slight irony and dark humor from left-oriented lovely jerks, formatted under the 'keywords' object as ` {{"fr": ["tag1", "tag2"]}} `.
    3. Keep the 'description' field under 50 characters.

    You must output a single valid JSON object containing an "events" key which is an array of objects matching this exact structure:
    {{
      "events": [
        {{
          "title": "...",
          "summary": "..." (optional),
          "description": "... (maximum 49 characters)",
          "longDescription": "..." (optional),
          "keywords": {{"fr": ["funnytag1", "funnytag2"]}},
          "registration": [{{"type": "link", "value": "https://..."}}] (optional),
          "timings": [{{"begin": "YYYY-MM-DDTHH:MM:SS", "end": "YYYY-MM-DDTHH:MM:SS"}}],
          "locationUid": integer or null
        }}
      ]
    }}

    Raw Event Descriptions:
    {json.dumps(descriptions, ensure_ascii=False, indent=2)}
    """

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    result = BatchEventOutput.model_validate_json(response.text)

    payloads = []
    for event in result.events:
        data = event.model_dump()
        data["timings"] = [
            {"begin": naive_str_to_paris_iso(t["begin"]), "end": naive_str_to_paris_iso(t["end"])}
            for t in data.get("timings") or []
        ]
        if data.get("locationUid") is None and default_location_uid is not None:
            data["locationUid"] = default_location_uid
        payloads.append(data)
    return payloads


def to_openagenda_event(payload: OpenAgendaEventPayload) -> dict:
    """Converts a generated payload into the body expected by the OA create event endpoint (multilingual fields)."""
    event: dict = {
        "title": {"fr": payload.title},
        "description": {"fr": payload.description},
        "timings": payload.timings,
    }
    if payload.longDescription:
        event["longDescription"] = {"fr": payload.longDescription}
    if payload.keywords:
        event["keywords"] = payload.keywords
    if payload.registration:
        event["registration"] = payload.registration
    if payload.locationUid is not None:
        event["locationUid"] = payload.locationUid
    return event