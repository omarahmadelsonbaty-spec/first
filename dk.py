import sqlite3

connect = sqlite3.connect("u.DB")
cursor = connect.cursor()

cursor.execute("SELECT e_id,solution,created_at FROM history WHERE e_id > 0")

rows = cursor.fetchall

for row in rows:
    print("|Number: " + row[0] , "\n|Solution: " + row[1] , "\n|Time: " + row[2])