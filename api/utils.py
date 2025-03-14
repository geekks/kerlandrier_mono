import os
import time
import json
import requests
from dotenv import load_dotenv
import jwt
import sqlite3
import bcrypt
from datetime import datetime, timedelta, timezone
import pytz
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv()

OA_TOKEN_FILE_NAME = "secret_token.json"
AGENDA_UID = os.getenv("AGENDA_UID")
OA_ACCESS_TOKEN_URL = os.getenv("ACCESS_TOKEN_URL")
OA_BASE_URL = os.getenv("OA_BASE_URL")
OA_PUBLIC_KEY = os.getenv("OA_PUBLIC_KEY")
OA_SECRET_KEY = os.getenv("OA_SECRET_KEY")
JWT_SECRET = "xxxxx"
JWT_ALGORITHM = "HS256"

db = sqlite3.connect("auth.db")

def verify_password(stored_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


async def retrieve_OA_access_token():
    # Check if token file exists and read it
    if os.path.exists(OA_TOKEN_FILE_NAME):
        try:
            with open(OA_TOKEN_FILE_NAME, "r", encoding='utf8') as token_file:
                token_data = json.load(token_file)
                if (
                    token_data
                    and token_data.get("access_token")
                    and token_data.get("endate")
                    and (token_data["endate"] - round(time.time()*1000)) > 0
                ):
                    return token_data["access_token"]
        except json.JSONDecodeError:
            print("Error reading token file: Corrupted file")

    # Else, request a new token
    print("Request a new token and save it in secret_token.json")
    headers = {
        "Content-Type": "application/json",
    }
    body = {
        "grant_type": "client_credentials",
        "code": OA_SECRET_KEY,
    }

    try:
        oauth_response = requests.post(OA_ACCESS_TOKEN_URL, json=body, headers=headers)
        oauth_response.raise_for_status()
        
        if oauth_response.status_code >= 200 and oauth_response.status_code <= 299:
            # Save token to local_storage (simulating a file save)
            token_data = {
            "access_token": oauth_response.json().get("access_token"),
            'endate': int(time.time()) + oauth_response.json()['expires_in'] - 600,  # 50m à partir de maintenant
            }
            with open(OA_TOKEN_FILE_NAME, "w") as token_file:
                json.dump(token_data, token_file)
                
            return token_data["access_token"]
        
    except requests.RequestException as exc:
        print("Error retrieving access token:", exc)

    print("[Retrieve accessToken] Error - no access token retrieved")
    return None

async def get_event_keywords(event_uid: str | int):
    uid = str(event_uid)
    url = f"{OA_BASE_URL}/agendas/{AGENDA_UID}/events/{uid}?key={OA_PUBLIC_KEY}"
    try:
        response = requests.get(url)
        if response.status_code >= 200 and response.status_code <= 299:
            data = response.json()
            keywords =  data.get('event', {}).get('keywords', {}).get('fr', None)
            if keywords is not None:
                return keywords
            else:
                return []
    except requests.RequestException as exc:
        print("Error getting event:", exc)
        if exc.response:
            print(exc.response)

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
            print("Error patching event:", response.json())
    except requests.RequestException as exc:
        logging.error(f"Error patching event: {exc}")

    return None

def generate_token(user_id: int) -> str:
    paris_tz = pytz.timezone('Europe/Paris')
    expiration_time = datetime.now(paris_tz) + timedelta(days=30)
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }
    logging.info(f"Token generated. Endate: {expiration_time}")
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token: str) -> dict:
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
    
def get_user_by_username(db, username):
    cursor = db.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    return cursor.fetchone()