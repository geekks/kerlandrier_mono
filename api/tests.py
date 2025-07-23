from libs.HttpRequests import get_locations
from libs.getOaLocation import get_or_create_oa_location
from script.configuration import config,oa

from script.mistral_images import  getMistralImageEvent
from script.libs.utils import  showDiff
import os
from wasabi import color,msg

def testMistralImages():
        TEST_FILE_NAME = "TEST_temps_foret.jpg"
        TEST_FILE_ANSWER = {"date_debut": "2025-01-31T20:00:00+01:00",
                            "description": ["documentaire","France","forêt",
                                            "bûcheron","scierie","débat","bois"],
                            "description_courte": ["Documentaire", "débat", "forêt"],
                            "duree": "0",
                            "heure_debut": "20:00",
                            "lieu": "Cinéville de CONCARNEAU",
                            "titre": "Le Temps des forêts"}
        MISTRAL_PRIVATE_API_KEY=config.MISTRAL_PRIVATE_API_KEY.get_secret_value()
        msg.info(f"Testing with {TEST_FILE_NAME}")
        image_path = os.path.join(os.path.dirname(__file__) , "sources", TEST_FILE_NAME)
        response_mistral=getMistralImageEvent(MISTRAL_PRIVATE_API_KEY,image_path)
        response_json = response_mistral.model_dump(mode='json')
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

#####################
## Test cases:
#####################

TBD_LOCATION_UID=config.TBD_LOCATION_UID

locations_examples = [
    {"input_location": 'MJC Tregunc Le Sterenn, Rue Jacques Prévert, 29910 Trégunc, France', "expectedUID": 89326663},
    {"input_location": 'Explore', "expectedUID": 5705265},
    {"input_location": "Bar de Test, 1 Pl. de l'Église, 29100 Pouldergat", "expectedUID": TBD_LOCATION_UID}, # Lieu inexistant mais ville existante
    {"input_location": 'qsdfg', "expectedUID": TBD_LOCATION_UID}, # Texte aléatoire
    {"input_location": '30 Rue Edgar Degas, 72000 Le Mans', "expectedUID": TBD_LOCATION_UID}, # HOrs Bretagne
    {"input_location": '11 Lieu-dit Quilinen 29510 Landrévarzec'}, # Non répertorié sur OA
    {"input_location": 'La Loco', "expectedUID": 34261153},
    {"input_location": 'Boulevard de la Gare, Quimperlé', "expectedUID": 34261153},
    {"input_location": 'La Caserne Concarneau ', "expectedUID": 9308588},
    {"input_location": '1 avenue Docteur NICOLAS, Concarneau'},
    {"input_location": 'Intermarché Concarneau (Route de Trégunc, Concarneau)', "expectedUID": 75052765},
    {"input_location": 'Brasserie Tri Martolod-Officiel', "expectedUID": 16309876},
    {"input_location": 'Rue de Colguen, 29900 Concarneau', "expectedUID": 24412066},
    {"input_location": 'Boulevard de la Gare, 29300 Quimperlé, France', "expectedUID": 34261153},
    
]

def test_locations(location_array: list,
                    public_key:str = oa.public_key,
                    access_token:str= oa.getToken(),
                    locations_api_url:str = f"{config.OA_API_URL}/locations"
                    ):
    allLocationsOA = get_locations(public_key, locations_api_url)
    allLocationsOA_by_uid = {item['uid']: item for item in allLocationsOA}
    nbr_locations= len(allLocationsOA)
    print(f"Number of locations: {nbr_locations}")
    for loc in location_array:
        uid = get_or_create_oa_location( searched_location=loc.get("input_location"),
                                        access_token=access_token,
                                        public_key=access_token,
                                        locations_api_url=locations_api_url,
                                        debug=True)
        if loc.get("expectedUID") and (loc.get("expectedUID") == uid): 
            print(" - ✅ Match with Expected location.")
        elif loc.get("expectedUID"): 
            print(" - ❌ Does not match with Expected location: '", allLocationsOA_by_uid.get (loc.get("expectedUID")).get("name"),"'")
        print("--------------\n")
