import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Log#3101Yt",
        database="delivery_system"
    )
