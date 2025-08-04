# manual_scripts.py
from script.import_ics import import_ics
from script.updateLocationsDescription import udpateLocationsDescription
from script.configuration import config, oa
from script.mistral_images import postMistralEvent

import argparse
import inquirer
import logging,coloredlogs
coloredlogs.install()

def main():
    parser = argparse.ArgumentParser(description="Run different scripts with arguments.")
    parser.add_argument('script', nargs='?', choices=['import_ics', 'updateLocationsDescription', 'postMistralEvent'],
                        help="The script to run.")
    parser.add_argument('--file', type=str, help="File path for postMistralEvent if source is File.")
    parser.add_argument('--url', type=str, help="URL for postMistralEvent if source is URL.")

    args = parser.parse_args()

    if args.script:
        # Use argparse for command-line arguments
        if args.script == 'import_ics':
            if args.url in ["kal","konkarlab"]:
                import_ics(config.URL_AGENDA_ATELIERS_KAL)
            else:
                import_ics(config.ICS_PRIVATE_URL_KLR_FB.get_secret_value())
        elif args.script == 'updateLocationsDescription':
            udpateLocationsDescription(oa.getToken(),
                                        oa.public_key,
                                        locations_api_url=f"{config.OA_API_URL}/locations")
        elif args.script == 'postMistralEvent':
            MISTRAL_PRIVATE_API_KEY = config.MISTRAL_PRIVATE_API_KEY.get_secret_value()
            access_token = oa.getToken()
            IMGBB_API_URL = config.IMGBB_API_URL
            IMGBB_PRIVATE_API_KEY = config.IMGBB_PRIVATE_API_KEY.get_secret_value()

            if args.file is not None and args.url is not None:
                parser.error("Cannot use both --file and --url arguments simultaneously.")
            if args.file is not None:
                postMistralEvent(
                    MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY,
                    access_token=access_token,
                    locations_api_url=f"{config.OA_API_URL}/locations",
                    public_key=oa.public_key,
                    image_path=args.file,
                    imgbb_api_url=IMGBB_API_URL,
                    imgbb_api_key=IMGBB_PRIVATE_API_KEY
                )
            elif args.url is not None:
                postMistralEvent(
                    MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY,
                    access_token=access_token,
                    public_key=oa.public_key,
                    locations_api_url=f"{config.OA_API_URL}/locations",
                    url=args.url,
                )
            else:
                parser.error("The --source argument is required for postMistralEvent.")
    else:
        # Use inquirer for interactive prompts
        questions = [
            inquirer.List('script',
                        message="Which script would you like to run?",
                        choices=['import_ics', 'updateLocationsDescription', 'postMistralEvent']),
            inquirer.List('ics_source',
                        message="Which ICS source would you like to import?",
                        choices=['Kerlandrier', 'Konkarlab'],
                        ignore=lambda x: x['script'] != 'import_ics' ),
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
            if answers['ics_source'] == 'Konkarlab':
                import_ics(config.URL_AGENDA_ATELIERS_KAL)
            else:
                import_ics(config.ICS_PRIVATE_URL_KLR_FB.get_secret_value())
        elif answers['script'] == 'updateLocationsDescription':
            udpateLocationsDescription(oa.getToken(), oa.public_key, locations_api_url=f"{config.OA_API_URL}/locations")
        elif answers['script'] == 'postMistralEvent':
            MISTRAL_PRIVATE_API_KEY = config.MISTRAL_PRIVATE_API_KEY.get_secret_value()
            access_token = oa.getToken()
            IMGBB_API_URL = config.IMGBB_API_URL
            IMGBB_PRIVATE_API_KEY = config.IMGBB_PRIVATE_API_KEY.get_secret_value()
            if answers['source'] == 'File':
                postMistralEvent(
                    MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY,
                    locations_api_url=f"{config.OA_API_URL}/locations",
                    access_token=access_token,
                    image_path=answers['file'],
                    imgbb_api_url=IMGBB_API_URL,
                    imgbb_api_key=IMGBB_PRIVATE_API_KEY
                )
            elif answers['source'] == 'URL':
                postMistralEvent(
                    MISTRAL_PRIVATE_API_KEY=MISTRAL_PRIVATE_API_KEY,
                    locations_api_url=f"{config.OA_API_URL}/locations",
                    access_token=access_token,
                    url=answers['url'],
                )

if __name__ == "__main__":
    main()
