"""_summary_
Valide tous les lieux ('location') d'OpenAgenda ("state": 1 )
"""

import logging
from libs.HttpRequests import (  
                            get_locations,
                            patch_location)

from .configuration import oa, config

def validate_locations(access_token: str, public_key: str, locations_api_url:str = f"{config.OA_API_URL}/locations"):
    accessToken = access_token
    allLocations= get_locations(public_key,locations_api_url)

    if allLocations and len(allLocations) > 0:
        validated_count = 0
        for location in allLocations :
            if location["state"] == 0:
                try:
                    patch_location(accessToken, str(location["uid"]), { 'state': 1 },locations_api_url)
                    logging.info("Validated location:", location["name"])
                    validated_count += 1
                except Exception as e:
                    logging.error(f"Error validating location: {location["name"]} - {location['uid']}")
                    logging.error(e)
        logging.info("Total validated locations:", validated_count)
        

if __name__ == "__main__":
    validate_locations(oa.getToken(), oa.public_key)
