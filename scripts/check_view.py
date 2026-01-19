import sqlite3

conn = sqlite3.connect('data/analysis.db')
cursor = conn.cursor()
cursor.execute("SELECT name, type FROM sqlite_master WHERE name='yb_stats'")
result = cursor.fetchall()
if result:
    print(f"yb_stats exists as: {result[0][1]}")
else:
    print("yb_stats does not exist")
conn.close()
