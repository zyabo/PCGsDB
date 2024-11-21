import pandas as pd
import mysql.connector
from mysql.connector import Error
from get_dir_paths import get_dir_paths
import os

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

def insert_into_table(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.executemany(query, data)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def S6_2_MYSQL():
    host = "localhost"
    user = "root"
    password = "PCGsDB"
    database = "PCGsDB"

    connection = connect_to_database(host, user, password, database)

    current_dir_path = os.path.dirname(os.getcwd())
    dir_paths = get_dir_paths(current_dir_path)
    file_path = os.path.join(dir_paths["datasets_dir"], 'PCGsDB.csv')
    data_frame = pd.read_csv(file_path)

    # If a column in your CSV is a boolean, make sure to convert it to a format suitable for MySQL.
    data_frame['CGC: Exist'] = data_frame['CGC: Exist'].astype(int)
    data_frame['DisGeNET: Exist'] = data_frame['DisGeNET: Exist'].astype(int)

    # Prepare SQL insert statement
    # Assume the table name is `pcgsdb_table` and the column names have been set to correspond to the columns of the CSV file
    query = """
    INSERT INTO pcgsdb_table (`ID`,`Tissue`,`Mutant Gene`,`Level`,`DisGeNET: Exist`,`DisGeNET: Min(Association Score)`,`DisGeNET: Max(Association Score)`,`CGC: Exist`,`CGC: Tier`,`CGC: GeneID`,`Evidences: Total number of evidence`,`Evidences: Total number of evidence(Associated)`,`Evidences: Total number of evidence(Not Associated)`,`Evidences: Total number of evidence(No Enough Information)`,`Evidences: Urls`,`Evidences: Scores(A:Ass., B: Not Ass., C: No Enough Information)`,`Cases: Number of Cases`,`Cases: Case No. of PMC-Patients`,`Cases: PMC PMIDs`,`Cases: PMC File Paths`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """


    # Prepare the data to be inserted and convert it into a list of tuples
    data_to_insert = [tuple(row) for row in data_frame.to_numpy()]

    # Insert data into the database table
    insert_into_table(connection, query, data_to_insert)

    #Close the database connection
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

if __name__ == "__main__":
    S6_2_MYSQL()
