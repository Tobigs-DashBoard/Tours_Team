import pymysql
from utils import logger
from queries import CREATE_INTINERARY, CREATE_INCLUSIONS, CREATE_FLIGHTS, CREATE_HOTELS, CREATE_PACKAGES


# DB connection function
def get_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='0422',
        db='tours_interpark',
        charset='utf8'
    )

def db_init():
    conn = get_connection()
    cur = conn.cursor()
    queries = [CREATE_PACKAGES, CREATE_FLIGHTS, CREATE_HOTELS, CREATE_INTINERARY, CREATE_INCLUSIONS]
    for query in queries:
        execute_db_query(conn, cur, query)
    conn.close()

# DB query execution function
def execute_db_query(conn, cur, query, params=None):
    try:
        cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        logger.info(f"INSERT 오류: {e}")
        if conn:
            conn.rollback()
        return False
    


