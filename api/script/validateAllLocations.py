"""_summary_
Valide tous les lieux ('location') d'OpenAgenda ("state": 1 )
"""

from libs.HttpRequests import (  
                            get_locations,
                            patch_location)

from configuration import  oa

def validate_locations():
    accessToken = oa.access_token
    allLocations= get_locations(accessToken)

    if allLocations and len(allLocations) > 0:
        validated_count = 0
        for location in allLocations :
            if location["state"] == 0:
                try:
                    response=patch_location(accessToken, str(location["uid"]), { 'state': 1 })
                    print("Validated location:", location["name"])
                    validated_count += 1
                except Exception as e:
                    print(f"Error validating location: {location["name"]} - {location['uid']}")
                    print(e)
        print("Total validated locations:", validated_count)
        

if __name__ == "__main__":
    validate_locations()