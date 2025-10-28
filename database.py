import mysql.connector
from config import DB_CONFIG

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        if self.connection is None:
            self.connection = mysql.connector.connect(**DB_CONFIG)
        return self.connection

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)  # чтобы получить результаты в виде словаря
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()