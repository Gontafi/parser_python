from datetime import datetime

import os.path
import requests
from bs4 import BeautifulSoup
from dateparser import parse
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "identifier.sqlite")

conn = sqlite3.connect(db_path)
c = conn.cursor()

resources = c.execute("SELECT * FROM resource").fetchall()

for resource in resources:
    try:
        response = requests.get(resource[2])
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.select(resource[3])

        for link in links:
            try:
                article_response = requests.get(link['href'])
                article_soup = BeautifulSoup(article_response.text, 'html.parser')

                title = article_soup.select_one(resource[4]).text.strip()
                content = article_soup.select_one(resource[5]).text.strip()
                date_str = article_soup.select_one(resource[6]).text.strip()
                date = parse(date_str)
                news_link = link['href']


                c.execute("INSERT INTO items (res_id, link, title, content, nd_date, s_date, not_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (resource[0], news_link, title, content, date.timestamp(), datetime.now().timestamp(), date.strftime('%Y-%m-%d')))
                conn.commit()
            except Exception as e:
                print(f"Error parsing news article: {str(e)}")

    except Exception as e:
        print(f"Error parsing news site: {str(e)}")


conn.close()
