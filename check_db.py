import sqlite3

conn = sqlite3.connect('aegis.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables in aegis.db:", [t[0] for t in tables])
conn.close()
