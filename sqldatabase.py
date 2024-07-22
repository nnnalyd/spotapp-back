import mysql.connector
from datetime import *
import os


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=f'sh689dvba10',
  database="mydatabase"
)

# With this module we are going to place user data into a sql database, data such as the last weekly playlist date
# , so we can create a weekly routine for a user

mycursor = mydb.cursor()

def insertData(id, startdate, nextdate):
    mycursor.execute(f"SELECT id FROM users WHERE id='{id}'")
    if mycursor.fetchall():
        print('Exists')
        return False
    else:
        sql = ('INSERT INTO users (id, startdate, nextdate) VALUES (%s, %s, %s)')
        val = (f"{id}", f"{startdate}", f'{nextdate}')

        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")
        return True

def getData():
    mycursor.execute("SELECT * FROM users")

    myresult = mycursor.fetchall()

    for x in myresult:
        print(x)

    for x in myresult:
        print(x)
        startdate = datetime.strptime(f'{x[1]}','%d%m%y')
        nextdate = datetime. strptime(f'{x[2]}','%d%m%y')

def returnDate(id, date):
    mycursor.execute(f"SELECT * FROM users WHERE id='{id}'")
    results = mycursor.fetchall()
    if results:
        print('found')
        for x in results:
            print(x)
            datenow = datetime.strptime(date, f'%d%m%y')
            nextdate = datetime. strptime(f'{x[2]}','%d%m%y')
            if nextdate == datenow:
                return True
            else:
                return False
    else:
        print('not found')


if __name__ == "__main__":
    returnDate('revilutiongames')

