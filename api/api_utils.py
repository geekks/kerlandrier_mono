import os,sys
import time
from fastapi import UploadFile
import requests

import jwt
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import pytz
import logging, coloredlogs

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from script.libs.oa_types import  OpenAgendaEvent
from script.mistral_images import getMistralImageEvent, mistralEvent
from script.libs.utils import check_image_file

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
                        url: str,
                        ) -> mistralEvent:
    try:
        response_mistral:mistralEvent = getMistralImageEvent(MISTRAL_PRIVATE_API_KEY, url=url)
        if response_mistral is None:
            return {"success": False, "message": "Error generating event on Mistral"}
    except Exception as e:
        logging.error(e)
        raise Exception(e)
    logging.info("Mistral answer:",response_mistral.model_dump(mode='json'))
    return response_mistral

def excerptOAEvent(OAevent: OpenAgendaEvent,
                    OA_AGENDA_URL: str = "https://openagenda.com/fr/kerlandrier"
                        ) -> dict:
    event_url= f"{OA_AGENDA_URL}/events/{OAevent.slug}"
    try:
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
    except Exception as e:
        raise Exception(f"Error exctracting info from OAevent: {e}")

def saveImagePost(file: UploadFile,
            upload_dir = "images"
            ) -> str:
    """
    Save an image from a request to a specified directory.
    Save the UploadFile type in a blocking (not async) way.
    
    Args:
        file (fastapi.UploadFile): The file to save.
        dir_path (str): The dir path where the file should be saved.
        
    Returns:
        str: The filepath.
    """
    if file is None:
        raise Exception("Please provide a file in a form-data")
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise Exception("File type not supported. Please upload a JPEG, PNG or GIF image.")
    if file.size > 5 * 1024 * 1024:  # 5 MB limit
        raise Exception("File size exceeds the limit of 5 MB.")
    try:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(file.file.read()) # Use not async way 
        if check_image_file(file_path) is False:
            raise Exception("Error: file is not an image")
        return file_path
    except Exception as e:
        raise Exception(f"Error saving file {file_path}: {e}")
