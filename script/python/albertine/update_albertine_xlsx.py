import json
import os
import pandas as pd
import sys
from pprint import pprint
sys.path.append(os.pardir) # Make sure local module imports work
import datetime
from libs.HttpRequests import retrieve_OA_access_token
from libs.HttpRequests import create_event
from configuration import config
SECRET_KEY = config.OA_SECRET_KEY.get_secret_value()

def parse_excel_file():
  columns = {
    'Quand ? ': "date_raw",
    'Quoi ? ': "title",
    'Où ? ': "location_raw",
    'Quels sujets ? ': "description_1",
    'Quelle forme ? ': "description_2",
    'Quels partenaires ? ': "description_3",
    '####': "keywords_raw"
  }

  locations = {
    "Librairie Albertine": "70555056",
    "Terrasse de la librairie": "70555056",
    "Catamaran Isabelle (Sailcoop), port de plaisance": "6643293"
  }
  # Define the file name
  file_name = "ANIMATIONS 2025.xlsx"
  sheet_name = 'Feuil1'
  
  # Get the current working directory
  cwd = os.getcwd()
  
  # Construct the full file path
  file_path = os.path.join(cwd, file_name)
  
  # Check if the file exists
  if not os.path.exists(file_path):
    print(f"File '{file_name}' not found in the current working directory: {cwd}")
    return
  
  # Read the Excel file
  excel_data = pd.ExcelFile(file_path)
  df = excel_data.parse(sheet_name)
  # Rename columns based on the mapping
  df = df.rename(columns=columns)
  
  # Handle 28/03/2025 15-18h & 04/04/2025 17h30-18h30
  # TODO: Ask two dedicated columns in input file
  df['date_raw'] = df['date_raw'].str.replace(r'-\d{2}h$', 'h', regex=True)
  df['date_raw'] = df['date_raw'].str.replace(r'-\d{2}h\d{2}$', '', regex=True)
  df['start_time'] = pd.to_datetime(df['date_raw'], errors='raise', dayfirst=True, format="mixed")
  df['end_time'] = df['start_time'] + pd.Timedelta(hours=2)

  df["location_code"] = df["location_raw"].map(locations)
  df['description_1'] = df['description_1'].fillna('')
  df['description_2'] = df['description_2'].fillna('')
  df['description_3'] = df['description_3'].fillna('')
  df['description'] = df['description_1'] + "\n" + df['description_2'] + "\n" + df['description_3']
  df['keywords'] = df['keywords_raw'].str.split('#').apply(lambda x: '-'.join([y.strip() for y in x if y.strip()]))

  df_oa = df[["start_time", "end_time", "title", "location_code", "description", "keywords"]]
  events_list = df_oa.to_dict(orient='records')
  
  log_content = []
  now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  try:
    access_token = retrieve_OA_access_token(SECRET_KEY)
  except Exception as e:
    print(f"Error retrieving the access token: {e}")
  
  
  try:
    for index, event in enumerate(events_list):
      timings = []
      timings.append({
        "begin": event.get('start_time').strftime("%Y-%m-%dT%H:%M:%S+0100"),
        "end": event.get('end_time').strftime("%Y-%m-%dT%H:%M:%S+0100")
      })
      new_oa_event = {
          "uid-externe": f"albertine_{file_name}-{index}",
          # "slug": slugify(event.get('title')),
          "title": {"fr": event.get('title')},
          "locationUid": int(event.get('location_code')) if event.get('location_code') else None,
          "locationTXT": event.get('location_raw'),
          "keywords": {"fr": event.get('keywords').split('-')},
          "description": {"fr": "-"},
          "longDescription": {"fr": event.get('description')},
          "timings": timings,
          "onlineAccessLink": "https://www.instagram.com/librairiealbertine/",
          "attendanceMode": 3,  # 1: physical, 2: online, 3: hybrid
      }
      eventLog = new_oa_event.copy()
      try:
        response = create_event(access_token, new_oa_event)
        if response['event']['uid']:
          print(f"New event: {event.get('title')}")
          print(f"OA URL: https://openagenda.com/fr/{response['event']['originAgenda']['slug']}/events/{response['event']['slug']}")
          eventLog["import_status"] = "New event"
          eventLog["uid"] = response['event']['uid']
          eventLog["OaUrl"] = f"https://openagenda.com/fr/{response['event']['originAgenda']['slug']}/events/{response['event']['slug']}"
        else:
          print(f"Problem for {event.get('title')}")
          eventLog["import_status"] = "Error posting event on OA"
          eventLog["error"] = response if response else "No response"
          print("--------")
      except Exception as e:
        print(f"Error while creating event: {e}")
        eventLog["import_status"] = "Error processing event"
        eventLog["error"] = str(e)
        print("--------")
      finally:
        if "import_status" in eventLog : log_content.append(eventLog)
  except Exception as e:
    print(f"Error while creating events: {e}")
  finally:
    with open(f"ics/import_ics_logs.txt", "a") as log_file:
          log_file.write(now + "\n")
          for dic in log_content:
              json.dump(dic, log_file,indent=2, ensure_ascii=False)
              if "error" in dic :
                  pprint(dic)  
    print("uids", [event.get("uid") for event in log_content if "uid" in event])
  

if __name__ == "__main__":
  parse_excel_file()