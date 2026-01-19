import sqlite3

conn = sqlite3.connect('data/analysis.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Current tables:")
for table in tables:
    print(f"  - {table[0]}")
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"    Rows: {count}")
conn.close()
