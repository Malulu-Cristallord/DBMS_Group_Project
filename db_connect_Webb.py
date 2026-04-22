# ======================
# 建立與 DB(mysql) 的連線
# ======================
import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="dbms_user",
            password="dbms1234",
            database="books_global"
        )
        return connection
    except Error as e:
        print("Database connection error:")
        print(e)
        return None