import sqlite3

dbName = "OlympicsData.db"
con = sqlite3.connect(dbName)
cur = con.cursor()

query = "SELECT COUNT(*) FROM SummerOlympics WHERE DONE_OR_NOT_DONE = 1"
cur.execute(query)
count = cur.fetchone()[0]
processes = con.total_changes
if count == 0:
    print("All rows are done")
else:
    print("Some processes are not done")

print("Number of processes working on the database: %i"%(processes))

query = "SELECT year FROM SummerOlympics"
cur.execute(query)
rows = cur.fetchall()
print(rows)


