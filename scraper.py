import urllib.request
import sqlite3
import json
from bs4 import BeautifulSoup
import random
import re
import unicodedata

dbName = "OlympicsData.db"

def scrape(cur, con):
    cur.execute("SELECT WikipediaURL, DONE_OR_NOT_DONE FROM SummerOlympics WHERE DONE_OR_NOT_DONE = 0")
    rows = cur.fetchall()
    for row in rows:
        url = row[0]
        done = int(row[1])
        if done == 0:
            
            cur.execute("UPDATE SummerOlympics SET DONE_OR_NOT_DONE = 1 WHERE WikipediaURL = ?", (url,))
            con.commit()
            
            req = urllib.request.Request(url, data=None, 
                                    headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64'})

            response = urllib.request.urlopen(req)
            body = response.read()

            soup = BeautifulSoup(body, 'html.parser')

            name = soup.find('span', class_ = "mw-page-title-main").get_text()

            year = name[:4]

            table = soup.find('table', class_ = "wikitable")

            rows = table.find_all('tr')

            city = rows[1].find('td').get_text()
            city = city.replace("\n", "")

            part_table = soup.find('table', class_ = "multicol")
            td_elements = part_table.find_all('td')

            sports = ""
            for td_element in td_elements:
                sport = td_element.find('ul').text
                sports += sport

            sports = sports.replace("\n", " ")
            sports = re.sub(r'\(\d+\)', "", sports)

            nations = ""

            tables = soup.find_all('table')
            for table in tables:
                if "Participating National Olympic Committees" in table.text:
                    nations += table.text

            nations = nations.replace("Participating National Olympic Committees", "")
            nations = nations.replace("\n\n", "")
            nations = nations.replace("\n", "")
            numbers_in_parentheses = re.findall(r'\((\d+)\)', nations)
            total = len(numbers_in_parentheses)
            atheles = sum(int(num) for num in numbers_in_parentheses)
            nations = re.sub(r'\(\d+.*?\)', "", nations)
            nations = unicodedata.normalize("NFKD", nations)
            ranks = []
            medal_table = soup.find('table', class_="plainrowheaders")
            table_rows = medal_table.find_all('tr')
            for i in range(1, 4):
                link =  table_rows[i].find('a',  attrs={'href': re.compile("^/wiki/")})
                ranks.append(link.text)
            con = sqlite3.connect(dbName)
            cur = con.cursor()
            query = """UPDATE SummerOlympics
           SET Name = ?,
               Year = ?,
               HostCity = ?,
               ParticipatingNations = ?,
               TotalNations = ?,
               Athletes = ?,
               Sports = ?,
               Rank_1_nation = ?,
               Rank_2_nation = ?,
               Rank_3_nation = ?,
               DONE_OR_NOT_DONE = ?
           WHERE WikipediaURL = ?"""

            data = (name, year, city, nations, total, atheles, sports, ranks[0], ranks[1], ranks[2], 1, url)
            cur.execute(query, data)

            con.commit()
            

con = sqlite3.connect(dbName)
cur = con.cursor()

scrape(cur, con)
query = "SELECT * from SummerOlympics"
result = cur.execute(query)
for row in result:
	print(row)
cur.close()

