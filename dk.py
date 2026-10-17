import sqlite3

connect = sqlite3.connect("u.DB")
cursor = connect.cursor()

cursor.execute("SELECT * FROM price")

f = cursor.fetchall()
print(f)

connect.close()