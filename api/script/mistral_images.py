"""
Script to get informations from an event poster with Mistral AI
Post Mistral Event to OpenAgenda
Examples:
python mistral_images.py --file TEST_temps_foret.jpg
python mistral_images.py --test
"""

import os
from mistralai import Mistral, SDKError
from pydantic import BaseModel
import pytz
from datetime import datetime
import requests
from urllib.parse import urlparse, urlunparse
from slugify import slugify
import argparse
from PIL import Image
from wasabi import color,msg
from dateparser import parse
import logging

    
from .libs.oa_types import OpenAgendaEvent
from .libs.utils import get_end_date, encodeImage64, check_image_file
from .libs.HttpRequests import create_event
from .libs.getOaLocation import get_or_create_oa_location

# Define a class to contain the Mistral answer to a formatted JSON
class mistralEvent(BaseModel):
    titre: str
    date_debut: str
    heure_debut: str
    duree: str
    lieu: str
    description: str
    description_courte: str
    fiabilite: int

def getMistralImageEvent(MISTRAL_PRIVATE_API_KEY:str, image_path:str=None, url:str = None)->mistralEvent:
    """
    Extracts event information from an image using Mistral AI.
    
    Args:
        image_path (str, optional): The file path of the image. Defaults to None.
        url (str, optional): The URL of the image. Defaults to None.
        
    Note:
        If both image_path and url are provided, the function will fail.
    
    Returns:
        Event: An mistralEvent object containing the extracted event information.
    """

    if url is not None and image_path is not None:
        logging.error("You can't use both image_path and url")
        return None
    if url:
        try:
        # Parse the URL to remove query parameters
            parsed_url = urlparse(url)
            clean_url = urlunparse(parsed_url._replace(query=""))
            file_name = os.path.join(os.path.dirname(__file__) , "images", os.path.basename(clean_url))
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_name, 'wb') as file:
                    file.write(response.content)
                image_path = file_name
                logging.info(f"Image downloaded and saved to {file_name}")
            else:
                raise Exception(f"Failed to download image. Status code: {response.status_code}",
                response.text)
        except Exception as e:
            raise Exception(f"Error downloading image from {url}", e)

    if not check_image_file(image_path):
        raise TypeError("Please provide a valid image file")

    try:
        if image_path and os.path.exists(image_path):
            Image.open(image_path).verify()
        else:
            raise FileNotFoundError(f"The image file {image_path} does not exist.")
    except Exception as e:
        raise Exception(f"Error verifying image: {e}")
        
    base64_image = encodeImage64(image_path)
    model = "pixtral-12b"
    client = Mistral(api_key=MISTRAL_PRIVATE_API_KEY)

    # Define the messages for the chat
    jour= datetime.now().strftime('%d/%m/%Y')
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Cette image est une affiche donnant des informations sur un évènement qui a lieu dans les prochains mois de cette année.\
                    Retourne moi un objet JSON contenant les information suivantes:\
                    titre,\
                    date_debut (date de début de l'évènement, qui sera dans les 12 mois à venir à partir du {jour}; elle sera au format ISO 8601. Le fuseau horaire utilisé sur l'affiche est celle de Paris. Par exemple, s'il est écrit 19h, il faudra mettre T19:00:00+02:00 en heure d'été et T18:00:00+01:00 en heure d'hiver)\
                    heure_debut (heure de début au format hh:mm),\
                    duree (durée de l'évenementau format hh:mm, avec 2 en durée par défaut si la durée n'est pas indisquée sur l'affiche),\
                    lieu (le nom du lieu ou l'adresse du lieu),\
                    description (les apostrophes sont notées avec le caractère ’ et pas '),\
                    description_courte (un résumé de l'évènement en 1 phrase),\
                    fiabilité: (un nombre entier entre 0 et 100 indiquant la fiabilité des informations extraites de l'affiche)"
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}" 
                }
            ]
        }
    ]
    logging.info("sending image to Mistral with image path: " + image_path)
    try:
        chat_response = client.chat.parse(
            model=model,
            messages=messages,
            response_format=mistralEvent
        )
        return chat_response.choices[0].message.parsed
    except SDKError as e:
        logging.error(f"SDKError while sending image to Mistral: {e.body}, {e.message}, {e.status_code}")
        raise Exception(f"SDKError while sending image to Mistral: {e.body}, {e.message}, {e.status_code}")
    except Exception as e:
        logging.error(f"Error while sending image to Mistral: {e}")
        raise Exception(f"Error while sending image to Mistral: {e}")

def postMistralEventToOa(event: mistralEvent,
                        access_token: str,
                        locations_api_url: str,
                        public_key: str = None,
                        image_url: str = None
                        ) -> OpenAgendaEvent|None:
    
    try:
        OaLocationUid = get_or_create_oa_location(searched_location = event.lieu,
                                                access_token = access_token,
                                                locations_api_url=locations_api_url,
                                                public_key=public_key)
        
    except Exception as e:
        logging.error(f"Error retrieving or creating location for event '{event.titre}': {e}")
        raise Exception(f"Error retrieving or creating location for event '{event.titre}': {e}")

    # Fixe la timezone à Paris pour prendre en compte l'heure d'été/hivert
    timezone_paris = pytz.timezone('Europe/Paris')
    localizedDateDeb = parse(event.date_debut).astimezone(timezone_paris).isoformat()
    eventOA= {
                "uid-externe": "mistral-" + slugify(event.titre),
                "title": { "fr": event.titre } ,
                "description": { "fr": event.description_courte},
                "locationUid": OaLocationUid,
                "longDescription": event.description,
                "timings": [
                        {
                        "begin": localizedDateDeb,
                        "end": get_end_date(parse(localizedDateDeb), event.duree).astimezone(timezone_paris).isoformat()
                        },
                        ]
            }
    if image_url:
        eventOA["image"] = {"url": image_url}
    try:
        response = create_event(access_token, eventOA)
        if response['event']['uid']:
                logging.info("Event created !")
                logging.info(f"OaUrl: https://openagenda.com/fr/{response['event']['originAgenda']['slug']}/events/{response['event']['slug']}")
                oaEvent = OpenAgendaEvent.from_json(response['event'])
                return  oaEvent
        else:
            logging.error( f"Problem for {event.titre}", response  )
            raise Exception(f"Error sending event to OA from Mistral. Response: {response}")
    except Exception as e:
        logging.error( f"Problem for event: '{event.titre}'")
        raise Exception(f"Error sending event to OA from Mistral: {e}")
        
def postImageToImgbb(image_path: str, imgbb_api_url: str , imgbb_api_key: str ) -> str|None:
    """
    Uploads an image to imgbb and returns the URL of the uploaded image.

    Args:
        image_path (str): The absolute path to the image file to be uploaded.

    Returns:
        str|None: The URL of the uploaded image if successful, otherwise None.
    """
    if not check_image_file(image_path):
        raise argparse.ArgumentTypeError(f"Given image path ({image_path}) is not valid")

    try:
        payload = {
            "expiration": 600,
            "key": imgbb_api_key,
            "name": os.path.basename(image_path),
            "image": encodeImage64(image_path)
        }
        response_imgbb = requests.post(imgbb_api_url, data=payload)
        image_url = response_imgbb.json()["data"]["image"]["url"] if response_imgbb.status_code == 200 else None
    except Exception as e:
        raise Exception(f"Error while uploading image to imgbb {e}")
    if image_url is None:
        raise Exception(f"Error while uploading image to imgbb : image_url is None {response_imgbb.text}")
    logging.info(f"Image uploaded to imgbb: {image_url}")
    return image_url


def postMistralEvent(MISTRAL_PRIVATE_API_KEY:str,
                    access_token:str,
                    public_key:str,
                    locations_api_url:str,
                    image_path:str=None,
                    url:str = None,
                    imgbb_api_url:str=None,
                    imgbb_api_key:str=None):
        if (url is not None) and (image_path is not None):
            raise Exception(f"You can't use both image_path and url")
        if image_path: # upload image to imgbb and get url
            try:
                image_url = postImageToImgbb(image_path,imgbb_api_url, imgbb_api_key)
                response_mistral = getMistralImageEvent(MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY, image_path=image_path)
                logging.info(response_mistral)
                OAEvent = postMistralEventToOa(response_mistral, access_token,locations_api_url, public_key, image_url)
            except Exception as e:
                raise Exception(f"Error processing image File: {e}")
        elif url:
            try:
                image_url=url
                response_mistral = getMistralImageEvent(MISTRAL_PRIVATE_API_KEY,url=image_url)
                logging.info(response_mistral)
                OAEvent= postMistralEventToOa(response_mistral,access_token,locations_api_url,public_key, image_url)
            except Exception as e:
                raise Exception(f"Error processing image URL: {e}")
        else:
            raise Exception(f"Enter a valid image path or url")
        if OAEvent is not None :
                return OAEvent
        else:
            raise Exception(f"Error: OAEvent is None. Check the image file {image_path} or url {url}")
    