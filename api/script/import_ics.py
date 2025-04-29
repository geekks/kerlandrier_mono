"""
Script to import events from a private Facebook calendar (ICS file)
"""
import json

import datetime
from pprint import pprint

from .configuration import config, oa

from .libs.ICS_utils import pull_upcoming_ics_events
from .libs.getOaLocation import get_or_create_oa_location
from .libs.HttpRequests import get_events, create_event

import argparse


now=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def import_ics(ics_url:str):
    """Main function to import ICS events."""
    # Fetch events from ICS
    
    # TO DO
    # Improve Text rendering, progress bar in console https://rich.readthedocs.io/en/stable/index.html
    
    # TO DO
    # Removed stylished text with weird fonts, like in https://yaytext.com/unstyle/
    # Unidecode ? https://pypi.org/project/Unidecode/

    ics_events = pull_upcoming_ics_events(ics_url)
    print(f"Total number of events on ICS : {len(ics_events)}\n")
    
    eventsOa: list=get_events(params={"relative[0]": "upcoming", "relative[1]": "current",
                                    "detailed": 1,
                                    "monolingual": "fr",
                                    "state[0]":2, "state[1]":1, "state[2]":0, "state[3]":-1} # get refused/removed events to avoid recreating it,
                            , oa_public_key=config.OA_PUBLIC_KEY
                            )
    print(f"Total number of future events on Oa : {len(eventsOa)}\n")
    uidsExterneOa = [event["uid-externe"] for event in eventsOa if "uid-externe" in event]
    
    new_events_nbr=0
    logContent=[]
    access_token = oa.access_token
    for i, ics_event in enumerate(ics_events):
        try:
            event_title = ics_event.get('title').get('fr')
            uidExterneIcsEvent = ics_event.get("uid-externe")
            if len(ics_event.get('description').get('fr')) <  3: ics_event['description']['fr'] = event_title
            # create event log in case of error
            eventLog = {
                    "ics-id": i,
                    "uid-externe" : uidExterneIcsEvent,
                    "title" : event_title,
                    "url": ics_event.get('onlineAccessLink')
                }
            # find if event is already imported.
            if uidExterneIcsEvent in uidsExterneOa:
                continue
            # Get OA location from facebook complete location infos (locationTXT)
            location_uid = get_or_create_oa_location(ics_event.get('locationTXT'), access_token)
            ics_event.update( {"locationUid": location_uid })
            ics_event.pop( "locationTXT" )
            
            #TODO: add a test function to check and add default values for alll parameters
            
            # Konk Ar Lab case
            if "konkarlab.bzh" in ics_url:
                if ics_event.get('locationUid') == config.TBD_LOCATION_UID:
                    ics_event.update( {"locationUid": config.KAL_LOCATION_UID} )
                ics_event['title']['fr'] = ics_event.get('title').get('fr').replace("[KAL] ", "")
                if (ics_event["onlineAccessLink"] == None) or ( ics_event["onlineAccessLink"].lower() in ("","none", "null")):
                    ics_event["onlineAccessLink"] = "https://www.konkarlab.bzh/infos-pratiques/agenda/"

            # Switch to physical event if no URL
            if (ics_event["onlineAccessLink"] == None) or ( ics_event["onlineAccessLink"].lower() in ("","none", "null")):
                ics_event.pop("onlineAccessLink")
                ics_event["attendanceMode"] = 1
            
            # Creates the event
            response = create_event(access_token, ics_event)
            if response['event']['uid']:
                eventLog["import_status"] = "New event"
                new_events_nbr += 1
                eventLog["OaUrl"] = "https://openagenda.com/fr/" + response['event']['originAgenda']['slug'] + "/events/" + response['event']['slug']
            else:
                print( f"Problem for {event_title}\n" )
                eventLog["import_status"] = "Error posting event on OA"
                eventLog["error"]= response if response else "No response"
            print("--------")
        except Exception as e:
            print(f"Error: {e} \n" )
            eventLog["import_status"] = "Error processing event"
            eventLog["error"]=  str(e)

        if "import_status" in eventLog : logContent.append( eventLog)
        
    with open(f"import_ics.log", "a") as log_file:
        log_file.write(now + "\n")
        for dic in logContent:
            json.dump(dic, log_file,indent=2, ensure_ascii=False)
            if "error" in dic :
                pprint(dic)
    print(f"Checked {i+1} events from ICS URL.")
    print(f"{new_events_nbr} new events created")

if __name__ == "__main__":
    
    parser=argparse.ArgumentParser()
    parser.add_argument("-u", "---URL", "--fileName",help="ICS URL to scan. Default to private Facebook's Kerlandrier page ICS")
    parser.add_argument("-t", "--test", required=False,help="Test command with {TEST_FILE_NAME}")
    args=parser.parse_args()
    match args.URL.lower():
        case None | ""|"facebook"|"fb"|"kerlandrier":
            icsUrl=config.ICS_PRIVATE_URL_KLR_FB
        case "kal"|"konkarlab":
            icsUrl=config.URL_AGENDA_ATELIERS_KAL
        case str() as url if url.startswith('https://'):
            icsUrl=url
        case _:
            exit(1,"Error with URL argument")
    import_ics(icsUrl)
