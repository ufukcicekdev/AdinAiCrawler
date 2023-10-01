
import os
import psycopg2
import psycopg2.extras
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

DB_NAME=os.getenv('DB_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')


class DBHelper(object):

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        

    def create_connection(self):
        cnx = psycopg2.connect(user=DB_USER,
                                  password=DB_PASSWORD,
                                  host=DB_HOST,
                                  port=DB_PORT,
                                  database=self.db_name
                    )
        cnx.autocommit = True
        return cnx

    
    def fetch(self, query: str) -> Dict:
        cnx = self.create_connection()
        cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        cnx.close()
        return rows

    def execute(self, query: str, data: Tuple) -> None:
        cnx = self.create_connection()
        cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, data)
        cur.close()
        cnx.close()

    def query(self, query: str) -> None:
        cnx = self.create_connection()
        cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query)
        cur.close()
        cnx.close()