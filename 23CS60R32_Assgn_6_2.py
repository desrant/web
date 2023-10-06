import urllib.request
import sqlite3
import json
from bs4 import BeautifulSoup
import random
import re
import unicodedata

def add_all(updated_links, cur):
    for link in updated_links:
        add_to_db(link, cur)

def add_to_db(url, cur):
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

    query = "INSERT INTO SummerOlympics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    data = (name, url, year, city, nations, total, atheles, sports, ranks[0], ranks[1], ranks[2])

    cur.execute(query, data)


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
first = random_values[0]
sec = random_values[1]

url1 = updated_links[first]
url2 = updated_links[sec]

dbName = "OlympicsData.db"
con = sqlite3.connect(dbName)
cur = con.cursor()

cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='SummerOlympics' ''')

if cur.fetchone()[0]==1:
	cur.execute("DROP TABLE SummerOlympics")

cur.execute("CREATE TABLE SummerOlympics(Name, WikipediaURL, Year, HostCity, ParticipatingNations, TotalNations, Athletes, Sports, Rank_1_nation, Rank_2_nation, Rank_3_nation)")

add_to_db(url1, cur)
add_to_db(url2, cur)

cur.execute("SELECT Year FROM SummerOlympics")
years = cur.fetchall()

year1, year2 = years[0][0], years[1][0]
print("Years Choosen:", year1, year2)

cur.execute("SELECT TotalNations FROM SummerOlympics WHERE Year = ?", (year1,))
total_nations1 = cur.fetchone()[0]

cur.execute("SELECT TotalNations FROM SummerOlympics WHERE Year = ?", (year2,))
total_nations2 = cur.fetchone()[0]

average_total_nations = (total_nations1 + total_nations2) / 2

print("Average Number of Countries in ", year1, "and", year2, ":", average_total_nations)

cur.execute("SELECT Rank_1_nation, Rank_2_nation, Rank_3_nation FROM SummerOlympics WHERE Year = ?", (year1,))
result1 = cur.fetchone()

# Query to retrieve the nations for Rank_1_nation, Rank_2_nation, and Rank_3_nation for the second year
cur.execute("SELECT Rank_1_nation, Rank_2_nation, Rank_3_nation FROM SummerOlympics WHERE Year = ?", (year2,))
result2 = cur.fetchone()

# Calculate the common nations (overlap) between the two years
common_nations = set(result1) & set(result2)

print("Common Nations between", year1, "and", year2, ":", common_nations)

cur.close()
