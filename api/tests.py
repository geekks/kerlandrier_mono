from script.configuration import config,oa

from script.import_ics import import_ics
from script.updateLocationsDescription import udpateLocationsDescription

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
