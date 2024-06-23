import mysql.connector
from datetime import *
import os

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=f'sh689dvba10',
  database="mydatabase"
)

current_date = datetime.now()
next_date = current_date + timedelta(days=7)

# With this module we are going to place user data into a sql database, data such as the last weekly playlist date
# , so we can create a weekly routine for a user

mycursor = mydb.cursor()


def insertData(id, startdate, nextdate):

    sql = ('INSERT INTO users (id, startdate, nextdate) VALUES (%s, %s, %s)')
    val = (f"{id}", f"{startdate}", f'{nextdate}')

    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def getData():
    mycursor.execute("SELECT * FROM users")

    myresult = mycursor.fetchall()

    for x in myresult:
        print(x)

if __name__ == "__main__":
    insertData('00000', '220022', '230022')
    getData()

