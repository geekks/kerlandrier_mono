# TO DO: launch differents scripts from this main file with prompt or arguments

from script.import_ics import import_ics
from script.updateLocationsDescription import udpateLocationsDescription
from script.configuration import config,oa
from script.mistral_images import postMistralEvent


import inquirer

# import_ics(config.ICS_PRIVATE_URL_KLR_FB.get_secret_value())

# udpateLocationsDescription(oa.access_token)

# fileName="images/sources/TEST_temps_foret.jpg"
# postMistralEvent(MISTRAL_PRIVATE_API_KEY=config.MISTRAL_PRIVATE_API_KEY.get_secret_value(),
#                 access_token=oa.access_token,
#                 image_path=fileName,
#                 imgbb_api_url=config.IMGBB_API_URL,
#                 imgbb_api_key=config.IMGBB_PRIVATE_API_KEY.get_secret_value()
#                 )

def main():
    questions = [
        inquirer.List('script',
                    message="Which script would you like to run?",
                    choices=['import_ics', 'updateLocationsDescription', 'postMistralEvent']),
        inquirer.List('source',
                    message="Do you want to send an URL or a local image To Mistral ?",
                    choices=['URL', 'File'],
                    ignore=lambda x: x['script'] != 'postMistralEvent' ),
        inquirer.Path('file',
                    message="Enter the file path for postMistralEvent",
                    path_type=inquirer.Path.FILE,
                    exists=True,
                    ignore=lambda x: (x['script'] != 'postMistralEvent' or  x['source'] == 'URL')),
        inquirer.Text('url',
                    message="Enter the URL for postMistralEvent",
                    ignore=lambda x:  (x['script'] != 'postMistralEvent' or  x['source'] == 'File'))
    ]

    answers = inquirer.prompt(questions)

    if answers['script'] == 'import_ics':
        import_ics(config.ICS_PRIVATE_URL_KLR_FB.get_secret_value())
    elif answers['script'] == 'updateLocationsDescription':
        udpateLocationsDescription(oa.access_token)
    elif answers['script'] == 'postMistralEvent':
        MISTRAL_PRIVATE_API_KEY=config.MISTRAL_PRIVATE_API_KEY.get_secret_value()
        access_token=oa.access_token
        IMGBB_API_URL=config.IMGBB_API_URL
        IMGBB_PRIVATE_API_KEY=config.IMGBB_PRIVATE_API_KEY.get_secret_value()
        if answers['source'] == 'File':
            postMistralEvent(
                MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY,
                access_token=access_token,
                image_path=answers['file'],
                imgbb_api_url=IMGBB_API_URL,
                imgbb_api_key=IMGBB_PRIVATE_API_KEY
            )
        elif answers['source'] == 'URL':
            postMistralEvent(
                MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY,
                access_token=access_token,
                url=answers['url'],
            )

if __name__ == "__main__":
    main()