"""
Script to get informations from an event poster with Mistral AI
Post Mistral Event to OpenAgenda
Examples:
python mistral_images.py --file TEST_temps_foret.jpg
python mistral_images.py --test
"""

import sys,os

from mistralai import Mistral
from pydantic import BaseModel
from pprint import pprint
import pytz
from datetime import datetime
from slugify import slugify
import argparse
from PIL import Image
from wasabi import color,msg
from dateparser import parse

# Ajoute le dossier "ressources" au sys.path
dir_file_path = os.path.dirname(os.path.abspath(__file__))
resources_path= os.path.join(dir_file_path,os.pardir, 'resources/python' ) 
print(f"Adding {resources_path} to sys.path")
try:
    sys.path.insert(0,resources_path )
except:
    print(f"Resouces not in parent directory/ Must be in Docker container. Adding  {dir_file_path} to sys.path")
    try:
        sys.path.insert(0,   dir_file_path )
    except Exception as e:
        msg.fail(f"An unexpected error occurred: {e}")
    
from utils import get_end_date, showDiff,encodeImage64
from HttpRequests import create_event, retrieve_access_token
from getOaLocation import get_or_create_oa_location
from  dateparser import parse


MISTRAL_PRIVATE_API_KEY = os.getenv("MISTRAL_PRIVATE_API_KEY")
SECRET_KEY = os.getenv("OA_SECRET_KEY")

# Define a class to contain the Mistral answer to a formatted JSON
class Event(BaseModel):
    titre: str
    date_debut: str
    heure_debut: str
    duree: str
    lieu: str
    description: str
    description_courte: str
    fiabilite: int

def getMistralImageEvent(image_path:str)->Event:

    try:
        Image.open(image_path).verify()
    except Exception as e:
        msg.fail(f"Image {image_path} is not valid image file")
        pprint(f"{e}")
        exit(1)
        
    base64_image = encodeImage64(image_path)
    model = "pixtral-large-latest"
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
                    date_debut (date de début de l'évènement, qui sera dans les 12 mois à venir à partir du {jour}; elle sera au format ISO. Le fuseau horaire utilsé sur l'affiche est celle de Paris)\
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
    with msg.loading("sending image to Mistral with image path: " + image_path):
        chat_response = client.chat.parse(
            model=model,
            messages=messages,
            response_format=Event
        )
    return chat_response.choices[0].message.parsed

def postMistralEventToOa(event: Event, image_path: str = None):
    
    access_token = retrieve_access_token(SECRET_KEY)
    OaLocationUid = get_or_create_oa_location(event.lieu, access_token)

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
    try:
        with msg.loading("Sending event to OpenAgenda"):
            response = create_event(access_token, eventOA, image_path)
        if response['event']['uid']:
                msg.good("Event created !")
                msg.info(f"OaUrl: https://openagenda.com/fr/{response['event']['originAgenda']['slug']}/events/{response['event']['slug']}")
        else:
            msg.fail( f"Problem for {event.titre}" )
            msg.fail( f"Response: {response}" )
    except Exception as e:
        msg.fail(f"Error sending event to OpenAgenda from Mistral analysis")
        msg.text( f"File: {image_path}. Event title '{response.titre}'")
        pprint(f"Error: {e}")

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-f", "--fileName", "--file", "--filename",help="Image file name in images/sources path ")
    parser.add_argument( "--test",nargs='?', const=True,help="Test command with {TEST_FILE_NAME}")
    args=parser.parse_args()
    
    if args.fileName:
        image_path = os.path.join(dir_file_path, "sources", args.fileName )
        if not os.path.isfile(image_path):
            raise argparse.ArgumentTypeError(f"Given image path ({image_path}) is not valid")
        response=getMistralImageEvent(image_path)
        response_json = response.model_dump(mode='json')
        print("Mistral answer:")
        pprint(response_json)
        postMistralEventToOa(response, image_path)
        
    elif args.test:
        # Test Part of the Program
        TEST_FILE_NAME = "TEST_temps_foret.jpg"
        TEST_FILE_ANSWER = {"date_debut": "2025-01-31T20:00:00+01:00",
                            "description": ["documentaire","France","forêt",
                                            "bûcheron","scierie","débat","bois"],
                            "description_courte": ["Documentaire", "débat", "forêt"],
                            "duree": "0",
                            "heure_debut": "20:00",
                            "lieu": "Cinéville de CONCARNEAU",
                            "titre": "Le Temps des forêts"}
        msg.info(f"Testing with {TEST_FILE_NAME}")
        image_path = os.path.join(dir_file_path, "sources", TEST_FILE_NAME)
        response=getMistralImageEvent(image_path)
        response_json = response.model_dump(mode='json')
        error=0
        for key in response_json:
            testPhrase=TEST_FILE_ANSWER.get(key)
            answerPhrase=response_json.get(key)
            # test value is a string
            if ( isinstance(testPhrase, str) and testPhrase.lower() not in str(answerPhrase).lower()):
                msg.fail(f"Test failed for:{key}")
                msg.info("Differences in answer vs expected:")
                print( showDiff(str(TEST_FILE_ANSWER.get(key)),
                                str(response_json.get(key))))
                error+=1
            # test values are an array of string (made dor long text like "description")
            if isinstance(testPhrase, list):
                for phrase in  TEST_FILE_ANSWER.get(key):
                    if str(phrase).lower() not in str(response_json.get(key)).lower():
                        msg.fail(f"Test failed for:{key}")
                        msg.info(f"Phrase {color(str(phrase), fg=120)} {color("not found in answer:", fg=4)} \
                                {color(str(response_json.get(key)), fg=80)}",
                                spaced = False
                                )
                        error+=1

        if error == 0:
            msg.good(f"Test passed for all keys !")
        else:
            msg.warn(f"Test failed for {error} of {len(TEST_FILE_ANSWER) + len(TEST_FILE_ANSWER.get("description")) - 1} keys")
        
    else:
        msg.fail(f"Please give a valid file name")
        exit(1)

    exit(0)