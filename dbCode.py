# dbCode.py
# Author: Your Name
# Helper functions for database connection and queries

import pymysql
import creds


def get_conn():
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        database=creds.db,
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, args=()):
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute(query, args)
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows

