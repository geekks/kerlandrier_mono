import math
import pandas as pd
import os
import json
from slugify import slugify
import datetime
import dateparser, pytz

def get_datetime_from_text(stringDate:str) -> datetime.datetime:
    "Convert a human readable string to datetime object"
    parsedDate = dateparser.parse(stringDate, languages=["fr"])
    # print("parsedDate: ", parsedDate)
    parisTZ = pytz.timezone("Europe/Paris")
    datetime = parisTZ.localize(parsedDate) if parsedDate else None
    # print("fromisoformat: ", isoDate)
    return datetime

def create_df():
    with open('maree_info_raw_dict.txt', 'r') as f:
        data = eval(f.read())
        # Convert the dictionary to a list of records with the date key as a new column
        records = []
        for date, entries in data.items():
            for entry in entries:
                entry['date'] = date  # Add the date as a new field
                records.append(entry)

        # Create a DataFrame from the records
        df = pd.DataFrame(records)

        # Reorder columns if needed, for example, placing 'date' as the first column
        df = df[['date', 'time', 'height', 'coef', 'tide']]

        # Save to pickle
        df.to_pickle('maree_info_raw.pkl')

        # Display the DataFrame
        print(df)
        return df

def format_df():
    try:
        df = pd.read_pickle('maree_info_raw.pkl')
    except:
        df = create_df()
    
    # Convert date column to datetime
    df['d'] = df['date']
    df['date'] = pd.to_datetime(df['date'])

    # Replace h by ':' in time column
    df['time'] = df['time'].str.replace('h', ':', regex=False)

   # Create datetime from date and time
    df['datetime_start'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    df['datetime_end'] = df['datetime_start'] + pd.Timedelta(minutes=1)


    # Add necessary columns to match
    # # title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name
    df['title'] = 'Grande marée (' + df['tide'].astype(str) + ")"
    # tide
    # height
    df['start_date'] = df['datetime_start'].dt.strftime('%Y-%m-%dT%H:%M:%s+0200')
    df['end_date'] = df['datetime_end'].dt.strftime('%Y-%m-%dT%H:%M:%s+0200')
    df['location_uid'] = 95821135
    df['link'] = 'https://www.maree.info/93?d=' + df['d']
    df['img'] = ""
    # cast to int
    df['coef'] = df['coef'].apply(lambda x: int(x) if not math.isnan(x)  else 0)
    df["location_name"] = ""



    print(df.head(2))
    print(df['coef'])

    # Save to pickle
    df.to_pickle('maree_info_format.pkl')
    return df

def format_csv():
    df = pd.read_pickle('maree_info_format.pkl')
    df = df[df['coef'] > 100]
    print(len(df))
    # Reorganize columns
    df = df[['title', 'tide', 'height', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'coef', 'location_name']]
    # # Target : "title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name"
    # Rename columns
    df.columns = ['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']

    print(df.head(2))
    df.to_csv('maree_info_format.csv', index=False, sep=';')

def format_oa():
    df = pd.read_pickle('maree_info_format.pkl')
    df = df[(df['coef'] > 100) & (df['tide'] == 'Basse')]
    print(len(df))
    json_list = []
    for index, row in df.iterrows():
        begin_datetime = get_datetime_from_text(f'{row["d"][0:4]}/{row["d"][6:8]}/{row["d"][4:6]} {row["time"]}')
        event = {
            "uid-externe": f"{row['title'].replace(' ', '_')}_{index}",
            "title": {"fr": row['title']},
            "slug": f'{slugify(row['title'])}-{index}',
            "description": {"fr": row['tide'] if row['tide'] else "-"},
            "longDescription": {"fr": f"{row['tide']}{f'\n{row['height']}' if row['height'] else ''}"},
            "timings": [
            {
                "begin": begin_datetime.strftime('%Y-%m-%dT%H:%M:%S+0200'),
                "end": (begin_datetime + datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%S+0200'),
            }
            ],
            "locationUid": row['location_uid'],
            "links": [{"link": row['link'], "data": {"url": row['link']}}],
            "image": {"url": row['img']},
            "keywords": {"fr": [f'Coef.{row["coef"]}', f'{row["height"]}m']},
            "onlineAccessLink": row['link'],
            "attendanceMode": 3 if row['link'] else 1,  # 1 physical, 2 online, 3 mixed
        }
        json_list.append(event)

    # Save to JSON file
    with open('maree_info_format.json', 'w') as f:
        json.dump(json_list, f, ensure_ascii=False, indent=4)


# create_df()
# format_df()
# format_csv()
format_oa()
