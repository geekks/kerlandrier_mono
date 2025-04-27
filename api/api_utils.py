import time
import requests

import jwt
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import pytz
import logging
from api.script.libs.oa_types import  OpenAgendaEvent
from api.script.mistral_images import getMistralImageEvent, postMistralEventToOa, mistralEvent


from api.script.configuration import config
from api.configuration import configAPI
from api.db import db_path

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AGENDA_UID = config.AGENDA_UID
OA_BASE_URL = config.OA_BASE_URL
OA_PUBLIC_KEY = config.OA_PUBLIC_KEY
JWT_SECRET = configAPI.JWT_SECRET.get_secret_value()
JWT_ALGORITHM = "HS256"
KAL_LOCATION_UID = config.KAL_LOCATION_UID
TBD_LOCATION_UID=config.TBD_LOCATION_UID

db: sqlite3.Connection = sqlite3.connect(db_path)

def verify_password(stored_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


async def get_event_keywords(event_uid: str | int):
    uid = str(event_uid)
    url = f"{OA_BASE_URL}/agendas/{AGENDA_UID}/events/{uid}?key={OA_PUBLIC_KEY}"
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

async def patch_event(access_token: str, event_uid: str | int, data: dict):
    uid = str(event_uid)
    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "access_token": access_token,
        "nonce": int(time.time() * 1000),  # Milliseconds since epoch
        "data": { "keywords": { "fr": data } },
    }
    url = f"{OA_BASE_URL}/agendas/{AGENDA_UID}/events/{uid}"
    try:
        response = requests.patch(url, json=body, headers=headers)
        if response.status_code >= 200 and response.status_code <= 299:
            return response.json()
        else:
            logging.error("Error patching event:", response.json())
    except requests.RequestException as exc:
        logging.error(f"Error patching event: {exc}")

    return None

def generate_kl_token(user_id: int) -> str:
    paris_tz = pytz.timezone('Europe/Paris')
    expiration_time = datetime.now(paris_tz) + timedelta(minutes=30)
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }
    logging.info(f"Token generated. Endate: {expiration_time}")
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_kl_token(token: str) -> dict:
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
    
def get_user_by_username(db: sqlite3.Connection, username:str):
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    return cursor.fetchone()

def send_url_to_mistral(MISTRAL_PRIVATE_API_KEY: str, access_token: str, url: str) -> dict:
    try:
        response_mistral:mistralEvent = getMistralImageEvent(MISTRAL_PRIVATE_API_KEY, url=url)
    except Exception as e:
        logging.error("Error generating event on Mistral",e)
        return {"success": False, "message": "Error generating event on Mistral"}
    logging.info("Mistral answer:",response_mistral.model_dump(mode='json'))
    try:
        OAevent:OpenAgendaEvent = postMistralEventToOa(response_mistral, access_token=access_token, image_url= url)
    except Exception as e:
        logging.error("Error generating event on OpenAgenda",e)
        return {"success": False, "message": "Error generating event on OpenAgenda"}
    try:
        event_url= f"https://openagenda.com/fr/{config.AGENDA_SLUG}/events/{OAevent.slug}"
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