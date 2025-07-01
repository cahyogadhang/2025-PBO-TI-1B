import sqlite3
import pandas as pd

DB_NAME = "pembelian.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def execute_query(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=(), fetch_all=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch_all:
        result = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in result]
    else:
        result = cursor.fetchone()
        if result:
            columns = [col[0] for col in cursor.description]
            result = dict(zip(columns, result))
    conn.close()
    return result

def get_dataframe(query, params=()):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df