import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('meiriyiwen.db')

# Get the cursor
cursor = conn.cursor()

# Get the table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the table names
for table in tables:
    print(table[0])
    print('-----------------')

# Close the cursor and connection
cursor.close()
conn.close()
