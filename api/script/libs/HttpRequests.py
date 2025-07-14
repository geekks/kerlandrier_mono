"""_summary_
Functions to interact with OpenAgenda API
"""

import logging
import os

import math, random
import requests, json
import time, pytz, dateparser


TOKEN_FILE_NAME = 'secret_token.json'
ACCESS_TOKEN_URL = "https://api.openagenda.com/v2/requestAccessToken"
LOCATIONS_API_URL = "https://api.openagenda.com/v2/agendas/44891982/locations"
EVENTS_API_URL = "https://api.openagenda.com/v2/agendas/44891982/events"

def get_nonce():
    """
    A timestamp + random number to be unique for each request, even those in short time interval (with same timestamp)
    """
    nonce = str(int(time.time())) + str(math.floor(random.random()*1000))
    return nonce
    

def retrieve_OA_access_token(OA_SECRET_KEY:str,
                            TOKEN_FILE_NAME:str = 'secret_token.json',
                            ACCESS_TOKEN_URL:str = ACCESS_TOKEN_URL
                            ) -> str:
    # Vérifier si le jeton existe déjà
    token_file_path = os.path.abspath(TOKEN_FILE_NAME)
    if os.path.exists(token_file_path):
        with open(token_file_path, 'r', encoding='utf8') as token_file:
            token_data = json.load(token_file)
            if (
                    token_data
                    and token_data.get("access_token")
                    and token_data.get("endate")
                    and (token_data["endate"] - round(time.time()*1000)) > 0
                ):
                    return token_data["access_token"]
        
    headers = {
        "Content-Type": 'application/json',
    }
    body = {
        "grant_type": "client_credentials",
        "code": OA_SECRET_KEY,
    }

    try:
        oauth_response = requests.post(ACCESS_TOKEN_URL,
                                    json=body,
                                    headers=headers)
        oauth_response.raise_for_status()

        token_data = {
            'access_token': oauth_response.json()['access_token'],
            'endate': int(time.time()) + oauth_response.json()['expires_in'] - 600,  # 50m à partir de maintenant
        }

        with open(token_file_path, 'w', encoding='utf8') as token_file:
            json.dump(token_data, token_file)

        return token_data['access_token']

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error retrieving access token: {exc}")
        return None

def get_locations(access_token: str,
                locations_api_url: str =LOCATIONS_API_URL):
    url = locations_api_url
    after =0
    all_locations=[]
    while after is not None:
        try:
            headers = {
                    "Content-Type": 'application/json',
                    "access-token": access_token,
                    "nonce": get_nonce()
                    }
            response = requests.get(url, headers=headers, params={'after': after, 'detailed': 1})
            response.raise_for_status()
            locations_part=json.loads(response.text)
            all_locations.extend(locations_part.get('locations'))
            after=locations_part.get('after')

        except requests.exceptions.RequestException as exc:
            logging.error(f"Error retrieving locations: {exc}")
            raise Exception(f"Error retrieving locations: {exc}")
    return all_locations

def post_location(access_token: str,
                name: str,
                adresse: str,
                locations_api_url: str=LOCATIONS_API_URL ):
    """
    Create a new location in OpenAgenda, using OA Geocoder with 'name' and 'address' as search parameters
    Args:
        access_token (str): The access token obtained by calling `retrieve_OA_access_token`
        name (str): The name of the new location
        adresse (str): The address of the new location
    Returns:
        JSON of the created location, under the key 'location'
    """
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = {
        "name": name,
        "address": adresse,
        "countryCode": "FR",
        "state": 0,  # signifie "non vérifié"
    }
    url = locations_api_url

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        text_json = json.loads(exc.response.text)
        if  text_json.get('message') != "geocoder didn't find address":
            logging.error(f"Error Posting location on OA: {exc}")
            raise Exception(f"Error Posting location on OA: {exc}")
        else:
            logging.warning(f"Geocoder didn't find address: {adresse}. Returning None")
            return None 

def patch_location(access_token:str,
                location_uid: str,
                body: dict,
                locations_api_url: str =LOCATIONS_API_URL):
    """
    Modify an  OpenAgenda location using a PATCH call. Only modified parameters are needed.
    Args:
        access_token (str): The access token obtained by calling `retrieve_OA_access_token`
        location_uid (str): The uid of the location
        body (dict): parameters to be updated. 
                {"uid"="aaa",{"description":{"fr":"AVEN"}}}
    }
    Returns:
        JSON of the updated location
    """
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    if (type(body) is not dict): 
        raise TypeError("body must be a dict")
    url = f"{locations_api_url}/{location_uid}"

    try:
        response = requests.patch(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json().get('location')

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error Patching location on OA: {exc}")
        return None


def delete_location(access_token: str,
                    location_uid: str,
                    locations_api_url: str = LOCATIONS_API_URL): 
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    url = f"{locations_api_url}/{location_uid}"

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error deleting location: {exc}")
        return None

def get_event(public_key: str,
            event_uid: str,
            events_api_url: str = EVENTS_API_URL) -> dict:
    """
    Retrieve an event from OpenAgenda API with given parameters.
    Args:
        access_token (str): The access token for the API call.
        event_uid (str): The uid of the event to retrieve.
    Returns:
        A dict of OA event.
    """
    headers = {
        "Content-Type": 'application/json',
        "nonce": get_nonce()
    }
    url = f"{events_api_url}/{event_uid}?key={public_key}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        logging.error(f"Error getting event: {exc}")
        return None

def get_events( params: dict,
            oa_public_key:str,
            events_api_url: str = EVENTS_API_URL) -> list:
    """
    Retrieve events from OpenAgenda API with given parameters.
    Args:
        params (dict): The parameters to pass to the API call.
            https://developers.openagenda.com/10-lecture/
            exemple: {'relative[]': 'current',
                    'search': 'conference',
                    'detailed': 1,
                    'monolingual': 'fr'}
    Returns:
        A list of OA events.
    """
    headers = {
        "Content-Type": 'application/json',
        "nonce": get_nonce()
    }
    url = f"{events_api_url}?key={oa_public_key}"
    after =0
    all_events=[]
    while after is not None:
        try:
            paramsUp =  params | {'after': after} if after != 0 else params
            response = requests.get(url,headers=headers,params=paramsUp)
            response.raise_for_status()
            events_part=json.loads(response.text)
            all_events.extend(events_part.get('events'))
            after=events_part.get('after')
        except requests.exceptions.RequestException as exc:
            logging.error(f"Error getting events: {exc}")
            return None
    return all_events


def create_event(access_token:str,
                event:dict,
                events_api_url: str = EVENTS_API_URL ):
    headers = {
        "Content-Type": "application/json",
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = event
    url = events_api_url
    try:
        event_creation_response = requests.post(url, json=body , headers=headers)
        if event_creation_response.status_code != 200:
            logging.error(f"Error creating event {event.get('title').get('fr')}: Status Code {event_creation_response.status_code}")
            logging.error(json.dumps(event_creation_response.json(), indent=4))
            return None
        
        createdEvent= json.loads(event_creation_response.text)['event']
        logging.info(f'New event: "{event['title']['fr']}" \
https://openagenda.com/kerlandrier/contribute/event/{str(createdEvent['uid'])}')
        return  event_creation_response.json()

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error creating event {event.get('title').get('fr')}: {exc}")
        return None

def patch_event(access_token:str,
                eventUid:str|int,
                eventData:dict,
                events_api_url: str = EVENTS_API_URL):
    headers = {
        "Content-Type": "application/json",
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    body = eventData
    url = f"{events_api_url}/{eventUid}"
    try:
        event_creation_response = requests.patch(url, json=body , headers=headers)
        logging.info(event_creation_response.json())
        if event_creation_response.status_code != 200:
            logging.error(f"Error pathcing event: Status Code {event_creation_response.status_code}")
            logging.error(json.dumps(event_creation_response.json(), indent=4))
            raise Exception(f"Error patching event: {event_creation_response.json().get('message', 'Unknown error')}")
        return  event_creation_response.json()

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error creating event: {exc}")
        return None

def delete_event(access_token:str,
                event_uid:str|int,
                events_api_url: str = EVENTS_API_URL):
    headers = {
        "Content-Type": 'application/json',
        "access-token": access_token,
        "nonce": get_nonce(),
    }
    url = f"{events_api_url}/{event_uid}"

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error deleting event: {exc}")
        return None

def search_events( oa_public_key: str, 
                search_string:str, 
                past_events:bool  = False, 
                other_params:dict = None, 
                events_api_url: str = EVENTS_API_URL ) -> dict | None:
    """
    Search events in the OpenAgenda API by a given search string.
    """
    headers = {
        "Content-Type": 'application/json',
        "key": oa_public_key,
    }
    params = {
        "search": search_string,
        "detailed": 1,
        "monolingual":"fr",
        "nonce": get_nonce()
    }
    if other_params is not None: params.update(other_params)
    if past_events is False : params['relative'] = ["current", "upcoming"]
    
    url = events_api_url
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        logging.error(f"Error getting events: {exc}")
        return None

def get_uid_from_name_date(oa_public_key:str,
                        event_name:str, 
                        text_date:str = None, 
                        uid_externe:bool = False) -> str|None:
    date = dateparser.parse(text_date)
    paris_zone = pytz.timezone('Europe/Paris')
    if date and date.tzinfo != 'Europe/Paris': date = date.astimezone(paris_zone)
    if date: 
        params={"timings":{
                        # TO DO: dynamic change in summer/winter time
                        "gte": date.strftime("%Y-%m-%dT00:00:00+02:00"),
                        "lte": date.strftime("%Y-%m-%dT23:59:59+02:00")
                        }
                    }

    search_result = search_events( oa_public_key,
                                event_name, 
                                past_events=True,
                                other_params=params)
    if search_result and search_result["events"]: 
        uid= search_result["events"][0].get("uid-externe") if uid_externe else search_result["events"][0].get("id")
        return uid
    return None

#####################
## Tests:
#####################

searchParamsTests = [
                    {
                    'relative[0]': 'current',
                    'detailed': 1,
                    'monolingual': 'fr'},
                    {
                    'relative[0]': 'current',
                    # 'relative[1]': 'upcoming',
                    'search': 'concert',
                    'detailed': 1,
                    'monolingual': 'fr'},
                    {
                    'relative[1]': 'upcoming',
                    'search': 'concert',
                    'detailed': 1,
                    'monolingual': 'fr'},
    
]
