import os,sys
import time
import requests

import jwt
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import pytz
import logging, coloredlogs

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from script.libs.oa_types import  OpenAgendaEvent
from script.mistral_images import getMistralImageEvent, postMistralEventToOa, mistralEvent
import typing

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
coloredlogs.install()
def verify_password(stored_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


def get_event_keywords(event_uid: str | int,
                            api_url: str,
                            oa_public_key: str ) -> list[str]:
    """
    Retrieves the French keywords associated with a specific event from the OpenAgenda API.

    Args:
        event_uid (str | int): The unique identifier of the event.
        api_url (str): The base URL of the OpenAgenda API.
        oa_public_key (str): The public key for accessing the OpenAgenda API.

    Returns:
        list[str]: A list of French keywords associated with the event. 
        Returns an empty list if no keywords are found or if the event does not exist.

    Raises:
        requests.RequestException: If there is an error making the API request or in input parameters.
    """
    uid = str(event_uid)
    if event_uid is None or api_url is None or oa_public_key is None:
        logging.error("Error event_uid, api_url or oa_public_key is None")
        raise ValueError("event_uid, api_url or oa_public_key is None")
        return None
    url = f"{api_url}/events/{uid}?key={oa_public_key}"
    try:
        response = requests.get(url)
        if response.status_code >= 200 and response.status_code <= 299:
            data = response.json()
            event: OpenAgendaEvent | None = data.get('event')
            if event:
                keywords: dict = event.get('keywords')
                if keywords:
                    fr_keywords: list[str]= keywords.get('fr')
                    if fr_keywords:
                        return fr_keywords
                    return []
                return []
            return []
    except requests.RequestException as exc:
        logging.error("Error getting event:", exc)
        if exc.response:
            logging.error("Response:", exc.response)

    return None

async def patch_event(access_token: str,
                    event_uid: str | int,
                    data: dict,
                    api_url: str
                    ):
    event_uid = str(event_uid)
    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "access_token": access_token,
        "nonce": int(time.time() * 1000),  # Milliseconds since epoch
        "data": { "keywords": { "fr": data } },
    }
    url = f"{api_url}/events/{event_uid}"
    try:
        response = requests.patch(url, json=body, headers=headers)
        if response.status_code >= 200 and response.status_code <= 299:
            return response.json()
        else:
            logging.error("Error patching event:", response.json())
    except requests.RequestException as exc:
        logging.error(f"Error patching event: {exc}")

    return None

def generate_kl_token(user_id: int,
                    JWT_SECRET: str,
                    JWT_ALGORITHM: str) -> str:
    paris_tz = pytz.timezone('Europe/Paris')
    expiration_time = datetime.now(paris_tz) + timedelta(days=30)
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }
    logging.info(f"Token generated. Endate: {expiration_time}")
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_kl_token(token: str,
                    JWT_SECRET: str,
                    JWT_ALGORITHM: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        logging.info("Token decoded successfully")
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logging.error("Invalid token")
        return None
    
def get_user_by_username(db: sqlite3.Connection,
                        username:str):
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def send_url_to_mistral(MISTRAL_PRIVATE_API_KEY: str,
                        access_token: str,
                        url: str,
                        OA_AGENDA_URL: str
                        ) -> dict:
    try:
        response_mistral:mistralEvent = getMistralImageEvent(MISTRAL_PRIVATE_API_KEY, url=url)
        if response_mistral is None:
            raise Exception("Error generating event on Mistral")
    except Exception as e:
        logging.error(e)
        return {"success": False, "message": "Error generating event on Mistral"}
    logging.info("Mistral answer:",response_mistral.model_dump(mode='json'))
    
    try:
        OAevent:OpenAgendaEvent = postMistralEventToOa(response_mistral, access_token=access_token, image_url= url)
    except Exception as e:
        logging.error("Error generating event on OpenAgenda",e)
        return {"success": False, "message": "Error generating event on OpenAgenda"}
    try:
        event_url= f"{OA_AGENDA_URL}/events/{OAevent.slug}"
        logging.info(f"OA event created: {OAevent.title.fr} at {OAevent.location.name}")
        return {"success": True, 
                "message": "OA event created successfully", 
                "event":{
                    "url": event_url,
                    "name": OAevent.title.fr,
                    "location": OAevent.location.name,
                    "description": OAevent.description.fr,
                    "start": OAevent.firstTiming.begin, 
                    "end": OAevent.firstTiming.end
                    }
                }
    except:
        logging.error("Error generating event on OpenAgenda", OAevent)
        return {"success": False, "message": "Error generating event on OpenAgenda"}
