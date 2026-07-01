import psycopg2
from psycopg2.extras import RealDictCursor
import time
from confg import DB_NAME,DB_USER,DB_PASSWORD,DB_HOST
while True:
    try:
        conn = psycopg2.connect(
            host = DB_HOST,
            database= DB_NAME,
            user = DB_USER,
            password = DB_PASSWORD,
            cursor_factory= RealDictCursor
        )
        cursor = conn.cursor()
        print("connected succesfully to the database")
        break
    except Exception as error :
        print("error:-" , error)
        time.sleep(2)
