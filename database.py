import os
import mysql.connector
from urllib.parse import urlparse


def get_connection():
    url = os.environ["MYSQL_URL"]
    parsed = urlparse(url)

    return mysql.connector.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip("/")
    )