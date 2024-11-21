import mysql.connector
from mysql.connector import Error

def connect_to_database(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def fetch_data(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            print(row)
        print(f"Total records retrieved: {len(results)}")
    except Error as e:
        print(f"The error '{e}' occurred")

def S6_3_MYSQL_Check():
    host = "localhost"
    user = "root"
    password = "PCGsDB"
    database = "PCGsDB"

    connection = connect_to_database(host, user, password, database)

    query = "SELECT * FROM pcgsdb_table"

    fetch_data(connection, query)

    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

if __name__ == "__main__":
    S6_3_MYSQL_Check()
