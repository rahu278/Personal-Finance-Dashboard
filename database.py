import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.environ["MYSQLHOST"],
        port=int(os.environ.get("MYSQLPORT", "3306")),
        user=os.environ["MYSQLUSER"],
        password=os.environ["MYSQLPASSWORD"],
        database=os.environ["MYSQLDATABASE"]
    )