"""_summary_"""

import sys,os
from git import Repo

# Ajoute le dossier "ressources" au sys.path
git_root = Repo(search_parent_directories=True).working_tree_dir
sys.path.insert(0,   os.path.abspath(  os.path.join(  git_root,'resources/python' ) ) )

import shutil, csv
import inquirer
from configuration import config

from HttpRequests import get_uid_from_name_date, get_events

csv_path: inquirer.Path  = ""
event_column_name: str = ""
data_list_dict: list[dict]    = []
validation: bool = False
home_path = git_root if git_root else "~/"

# Load CSV data to Dict
def read_csv_events(file_name_path:str) -> tuple[list[dict], list[str]]:
    try:
        with open(file_name_path, "r", encoding='utf-8') as file:
            dictreader = csv.DictReader(file, delimiter=';')
            csv_header = dictreader.fieldnames
            event_list: list[dict] = [ row for row in dictreader]
            
            return event_list, csv_header
    except csv.Error as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


# Get first 3 values of a column in CSV to show it to user for validation
def get_first_lines(event_column_name:str, data_list_dict:list[dict]) -> list[dict]:
    try:
        return [entry[event_column_name] for entry in data_list_dict[:3] ]
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction des données : {e}")



csv_path = inquirer.prompt(questions=[
                inquirer.Path(
                    name="csv_path",
                    message="Enter csv file path containing events wihtout their OA UID",
                    default= f"{home_path}/api/script/scraping/archipel_fouesnant/2024/archipel_format.csv",
                    exists=True, 
                    path_type=inquirer.Path.FILE
                )
            ]
    )

# create backup
shutil.copyfile( csv_path['csv_path'], csv_path['csv_path'] + ".bak", follow_symlinks=True)

# Première ligne du CSV pour récupérer les noms des colonnes
csv_header = read_csv_events(csv_path['csv_path'])[1]

# Liste des events
event_list = read_csv_events(csv_path['csv_path'])[0]



event_column_name  = inquirer.prompt( questions=[
                    inquirer.List(
                        name="event_column_name",
                        message= "select a column containing the event name (to search it in OA events)",
                        choices= csv_header
                    )
                ]
        )

# First titles events
title_examples=get_first_lines(event_column_name['event_column_name'], event_list)
title_examples_shorten = ",\n -".join(title_examples[:3])

print(f"First 3 events in CSV file:\n -{title_examples_shorten}")

validation = inquirer.prompt( questions=[
                inquirer.Confirm(
                    name="validation",
                    message=f"Does it look correct?",
                    default= True,
                )
            ]
)


if (not validation['validation']) : exit(0)


for row in event_list:
    event_uid = get_uid_from_name_date(
                    row[event_column_name['event_column_name']],
                    row['start_date'].split("T")[0]
                    )
    if event_uid:
        existing_event = get_events(
                            params={"uid": event_uid}
                            )[0]
    if existing_event:
        existing_event_title = existing_event.get('title', {}).get('fr', "NOT FOUND")

    print(f"event_name: {row[event_column_name['event_column_name']]} ---- existing event name----- {existing_event_title}")