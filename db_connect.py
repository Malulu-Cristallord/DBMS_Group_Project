import mysql.connector

# Create the connection object
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="your_password",
    database="db"
)

# Verify connection
if db_connection.is_connected():
    print("Successfully connected to the database")
