"""_summary_
WIP:
Permet de récupérer les infos des événements Facebook en scrapant les pages à l'aide de Playwright
"""

import json, re, os
from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

urls = [
    "https://www.facebook.com/lamaison.concarneau"
    # "https://www.facebook.com/events/2318886078470059/"
]

eventsUrls = ["https://www.facebook.com/events/1276047210369476/"]

dir_file_path = os.path.dirname(os.path.abspath(__file__))

with open( os.path.join( dir_file_path, 'facebook.cookies.json'), 'r') as file:
    cookies = json.load(file).get("cookies")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    context.add_cookies(cookies)     
    # for url in urls:
    #     page = context.new_page()
    #     print(f"Going to page': '{url}")
    #     page.goto(url, referer = 'https://www.facebook.com/')
    #     time.sleep(3)

        # soup = BeautifulSoup(page.content(), 'html.parser')

        # element_list = soup.find_all('a', attrs={"href": re.compile("^https://www.facebook.com/events/")})
        # for element in element_list:
        #     eventsUrls.append(element.attrs['href'].split('?')[0])
        
        # eventsUrls = list(dict.fromkeys(eventsUrls)) # deduplicate URLs
        # print(f"Finished scraping {url}")
        # print(f"Found:")
        # pprint.pprint(eventsUrls)

    for eventUrl in eventsUrls:
        print(f"Going to page': '{eventUrl}")
        page = context.new_page()
        page.goto(eventUrl, referer = 'https://www.facebook.com/')
        time.sleep(3)
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        interestedButtons = soup.find_all( lambda tag: tag.name == "span" and re.search("^Intéress", tag.text ))
        caminteresseButtons = soup.find_all( lambda tag: tag.name == "span" and re.search("^Ça m’intéresse", tag.text ))
        caminteresseButtons2 = soup.find('div', attrs={"aria-label": "Ça m’intéresse"})
        
        page.get_by_text("Ça m’intéresse").first.click()
        time.sleep(2)
    browser.close()

print("Scraping completed for all URLs.")