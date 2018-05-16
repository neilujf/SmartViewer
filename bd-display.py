
import sqlite3

CreateDataBase = sqlite3.connect('SmartViewer.db')

QueryCurs = CreateDataBase.cursor()

QueryCurs.execute('SELECT * FROM Image')

for i in QueryCurs:
    print("\n")
    for j in i:
        print(j)

QueryCurs.close()
