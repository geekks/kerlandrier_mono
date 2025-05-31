from libs.HttpRequests import get_events, create_event
import json
from configuration import config, oa

def parse_json(file_path):
  with open(file_path, 'r') as file:
    data = json.load(file)
  return data

# TODO: Parametrize file_path via args
file_path = 'scraping/2025_maree_info/maree_info_format_heure_hiver_ok.json'
parsed_data = parse_json(file_path)

access_token = oa.access_token
print(access_token)

createdEventUids = []
createdEventLinks = []

for event in parsed_data:
  print(event)
  response = create_event(access_token, event)
  if response['event']['uid']:
    # TODO: Proper logging cf. import_ics.py
    createdEventUids.append(response['event']['uid'])
    createdEventLinks.append("https://openagenda.com/fr/" + response['event']['originAgenda']['slug'] + "/events/" + response['event']['slug'])
    print("uids",createdEventUids)
    print("links", createdEventLinks)
  print(response)
# event