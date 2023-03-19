from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateparser import parse
import sqlite3

conn = sqlite3.connect('identifier.sqlite')
c = conn.cursor()

resources = c.execute('SELECT * FROM "resource"').fetchall()

for resource in resources:
    response = requests.get(resource[2])
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.select(resource[3])

    for link in links:
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

conn.close()