import sqlite3

connect = sqlite3.connect("u.DB")
cursor = connect.cursor()

cursor.execute("SELECT id, solution, created_at FROM history WHERE id > 0")

# Added parentheses to execute the fetch function
rows = cursor.fetchall()

for row in rows:
    # Used f-string formatting to prevent type concatenation errors
    print(f"|Number: {row[0]}\n|Solution: {row[1]}\n|Time: {row[2]}\n-----------------")

connect.close()