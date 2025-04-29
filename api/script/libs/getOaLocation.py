"""_summary_
Functions to manage locations with OA API
"""


from .utils import *
from .scraping_utils import *
from .HttpRequests import post_location, retrieve_OA_access_token, delete_location, get_locations

from thefuzz import fuzz
from thefuzz import process
import re

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TBD_LOCATION_UID="11634941"

def get_or_create_oa_location(searched_location:str, access_token: str, debug:bool=False, TBD_LOCATION_UID:str=TBD_LOCATION_UID)->str:
    """
    Tries to find a matching OpenAgenda location for the given searched location.
    Returns an OALocation UID (found, created or default one.)
    """
    logger.info(f"- searching location for : '{searched_location}'")
    if (searched_location == None ) or (searched_location.lower() in ( "" , "none", "null")):
        logger.warning("InputLocation is null or empty. Returning default Location")
        return TBD_LOCATION_UID
    allOaLocations = get_locations(access_token)
    if not searched_location or not allOaLocations:
        logger.error("[ERROR] inputLocation is null or OA Locations list is empty")
        return None
    
    # 0) Use optimized searched, removing false positives and misleadings patterns
    searched_location=re.sub(r'\b(?:concarneau|finistère|france|officiel|spectacles)\b',
                                            '',
                                            searched_location,
                                            flags=re.IGNORECASE
                                            )
    searched_location=re.sub(r'[-,():]',' ',
                                            searched_location,
                                            flags=re.IGNORECASE
                                            )
    # Postal code Finistere
    searched_location=re.sub(r'\b29\d{3}\b','',searched_location)
    # Remove double spaces
    searched_location=searched_location.strip()
    searched_location=re.sub(r'  ',     ' ',searched_location)
    
    # TO DO: add this specific cases to a config file
    try:
        replacement = [
        ("Boulevard de la Gare Quimperlé", "La Loco Quimperlé"),
        ("ZA de Colguen Rue Aimé Césaire", "Brasserie Tri Martolod Concarneau"),
        ("Rue Jacques Prévert Trégunc", "Le Sterenn Trégunc"),
        ("Brasserie de Bretagne Le Bek", "Le Bek"),
        ("Rue de Colguen", "Cinéville, Rue de Colguen"),
        ("LE CAFE LOCAL", "Le Café Local, Combrit"),
        ("3e lieu l'Archipel", "l'Archipel, Fouenant"),
        ("1 place Jean Jaures","Le livre & la plume"),
        ("CAC Scènes", "Le CAC"),
        ("Médiathèque de Fouesnant  l'Archipel", "L'Archipel, 1 Rue des Îles, Fouesnant")
    ]
        for old, new in replacement:
            searched_location = searched_location.replace(old, new)
    except Exception as e:
        logger.error(f"Error in Location replacement: {e}")
        
    if searched_location in ["", " ", "  ", "None", "Null", "Concarneau", None]:
        searched_location = "Concarneau (lieu à préciser)" 
    
    optimized_searched_location = searched_location
    logger.info(" (optimized name for better matching:  '"+ optimized_searched_location +"')")
    # 1) Try to find an existing OALocation
    OaLocationsIndex = {}
    for location in allOaLocations:
        OaLocationsIndex[location["uid"]]=location['name'] + " " + location['address']
    # returns a list of tuples (name adress , score , OAuid)
    results = process.extract(optimized_searched_location, OaLocationsIndex, scorer=fuzz.token_set_ratio) or []
    if results[0] and results[0][1] > 85:  # Best matching score >85
        logger.info(f"- 🎯 Location found in OA: {results[0] }")
        return results[0][2]

    # 2) Try to create an OALocation
    response = post_location(access_token,  name = searched_location, adresse=searched_location)
    if not response or not response.get('location', {}).get('uid'):
        logger.warning("-> ❔ Returning location 'To be defined' (Could not create location on OpenAgenda)")
        return TBD_LOCATION_UID

    # Stay in rectangle covering Breizh
    new_oa_location = response['location']
    lat = new_oa_location['latitude']
    long = new_oa_location['longitude']
    if ( new_oa_location.get('uid')        
        and 47 < float(lat) < 49
        and -5.5 < float(long) < -1 
        ):
        logger.info(f"-> '\U0001f195' New OA location created : {new_oa_location['name']}, {new_oa_location['address']}, {"https://openagenda.com/kerlandrier/admin/locations/" + str(new_oa_location['uid'])}")
        return new_oa_location['uid']
    else:
        delete_location(access_token, new_oa_location['uid'])
        logger.warning(f"-> ❔ Location not in Breizh: returning 'To be defined' location")
        return TBD_LOCATION_UID

def get_locations_list(searched_location:str, access_token: str)->list:
    """
    Return list of matching locations in format ('NAME, ADRESS, SCORE [0-100], UID)
    """
    allOaLocations = get_locations(access_token)
    if not searched_location or not allOaLocations:
        logger.warning("[ERROR] inputLocation is null or OA Locations list is empty")
        return None
    
    # 1) Try to find an existing OALocation
    OaLocationsIndex = {}
    for location in allOaLocations:
        OaLocationsIndex[location["uid"]]=location['name'] + " " + location['address']
    # returns a list of tuples (name adress , score , OAuid)
    results = process.extract(searched_location, OaLocationsIndex, scorer=fuzz.token_set_ratio) or []
    
    
    if len(results): 
        if results[0][1] >= 80:  # Best matching score >85
            return results[0]
        # good_results = [item for item in results if item["score"] > 70]
        return results[:5]
    else:
        return None


