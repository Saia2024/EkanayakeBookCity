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
        connection = cls.get_connection()
        if connection is None:
            return None
        cursor = connection.cursor(dictionary=True) 
        try:
            cursor.execute(query, params)
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            else: 
                connection.commit()
                result = cursor.lastrowid or cursor.rowcount 
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
