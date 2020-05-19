import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

create_table = "CREATE TABLE users (id int, username text, password text)"
cursor.execute(create_table)

# queries
insert_query = "INSERT INTO users VALUES (?, ?, ?)"
select_query = "SELECT * FROM users"

# Insert single record
user = (1, 'John', '12345')
cursor.execute(insert_query, user)

# Insert records
users = [
    (2, 'Brad', '12345'),
    (3, 'Mark', '12345'),
]

cursor.executemany(insert_query, users)

# Select Records
for row in cursor.execute(select_query):
    print(row)

connection.commit()
connection.close()
