import urllib.request
import sqlite3
import json
from bs4 import BeautifulSoup
import random
import re
import os
import multiprocessing as mp

dbName = "OlympicsData.db"

def donezero(updated_links, cur):
     for link in updated_links:
        cur.execute("INSERT INTO SummerOlympics (WikipediaURL, DONE_OR_NOT_DONE) VALUES (?, ?)", (link, 0))
        con.commit()

url = "https://en.wikipedia.org/wiki/Summer_Olympic_Games"
req = urllib.request.Request(url, data=None, 
                             headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64'})

response = urllib.request.urlopen(req)
body = response.read()

soup = BeautifulSoup(body, 'html.parser')


table = soup.find('table', class_ = "sortable wikitable")

rows = table.find_all('tr')

links = []

for row in rows:
    link =  row.find('a',  attrs={'href': re.compile("^/wiki/")})
    if(link):
        name = link.get('href')
        links.append(str(name))

updated_links = []
    
for link in links:
    new = "https://en.wikipedia.org" + link
    updated_links.append(new)


updated_links = updated_links[24:32:]

size = len(updated_links)
random_values = random.sample(range(size), 2)

con = sqlite3.connect(dbName)
cur = con.cursor()

cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='SummerOlympics' ''')

if cur.fetchone()[0]==1:
    cur.execute("DROP TABLE SummerOlympics")


cur.execute("CREATE TABLE SummerOlympics(Name, WikipediaURL, Year, HostCity, ParticipatingNations, TotalNations, Athletes, Sports, Rank_1_nation, Rank_2_nation, Rank_3_nation, DONE_OR_NOT_DONE)")

donezero(updated_links, cur)

os.system("python3 scraper.py&")


