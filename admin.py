import sqlite3
connection = sqlite3.connect("my_database")

while True:
    statement = input()
    if statement == 'q':
        break
    elif statement == 'c':
        connection.commit()
    else:
        ret = connection.execute(statement)
        if ret.description != None:
            print([val[0] for val in ret.description])
        for row in ret.fetchall():
            print(row)
        print()
        