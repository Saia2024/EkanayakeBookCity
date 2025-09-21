import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or not cls._connection.is_connected():
            try:
                cls._connection = mysql.connector.connect(**DB_CONFIG)
                print("MySQL Database connection successful")
            except Error as e:
                print(f"Error '{e}' connecting to MySQL database")
                cls._connection = None
        return cls._connection

    @classmethod
    def execute_query(cls, query, params=None, fetch=None):
        """
        Executes a query and returns results.
        :param query: SQL query string
        :param params: A tuple of parameters for the query
        :param fetch: 'one' for a single record, 'all' for multiple records
        """
        connection = cls.get_connection()
        if connection is None:
            return None
        cursor = connection.cursor(dictionary=True) # dictionary=True is very useful!
        try:
            cursor.execute(query, params)
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            else: # For INSERT, UPDATE, DELETE
                connection.commit()
                result = cursor.lastrowid or cursor.rowcount # Return new ID or rows affected
            return result
        except Error as e:
            print(f"Query failed: '{e}'")
            return None
        finally:
            cursor.close()

    @classmethod
    def close_connection(cls):
        if cls._connection is not None and cls._connection.is_connected():
            cls._connection.close()
            print("MySQL connection is closed")