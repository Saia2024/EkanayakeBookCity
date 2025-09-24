import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    _connection = None  # Holds a single database connection for reuse

    @classmethod
    def get_connection(cls):
        # Create a new connection only if none exists or it's disconnected
        if cls._connection is None or not cls._connection.is_connected():
            try:
                cls._connection = mysql.connector.connect(**DB_CONFIG)  # Connect using config details
                print("MySQL Database connection successful")
            except Error as e:
                print(f"Error '{e}' connecting to MySQL database")  # Print connection error
                cls._connection = None
        return cls._connection  # Return the active connection

    @classmethod
    def execute_query(cls, query, params=None, fetch=None):
        connection = cls.get_connection()  # Get or create a connection
        if connection is None:
            return None
        cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for results
        try:
            cursor.execute(query, params)  # Run the query with optional parameters

            # Decide how to handle results based on 'fetch' option
            if fetch == 'one':
                result = cursor.fetchone()  # Get single row
            elif fetch == 'all':
                result = cursor.fetchall()  # Get all rows
            else: 
                connection.commit()  # For insert/update/delete, commit changes
                result = cursor.lastrowid or cursor.rowcount  # Return new ID or affected rows
            return result
        except Error as e:
            print(f"Query failed: '{e}'")  # Print error if query fails
            return None
        finally:
            cursor.close()  # Always close cursor after use

    @classmethod
    def close_connection(cls):
        # Close the connection if it exists and is still open
        if cls._connection is not None and cls._connection.is_connected():
            cls._connection.close()
            print("MySQL connection is closed")
