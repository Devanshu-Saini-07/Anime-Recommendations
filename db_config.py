import mysql.connector

def connect():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="anime_tracker"
    )