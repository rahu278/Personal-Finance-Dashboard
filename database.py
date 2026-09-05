import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "localhost"),
        port=int(os.getenv("MYSQLPORT", "3306")),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", "Rahul@8888"),
        database=os.getenv("MYSQLDATABASE", "finance_db")
    )
