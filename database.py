import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rahul@8888",
        database="finance_db"
    )

    return connection