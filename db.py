import os
import pymysql
from pymysql.cursors import DictCursor
from config import Config

def get_db_connection(database=True):
    """
    Establish a connection to MySQL.
    If database=False, connects without specifying the DB (useful for initial creation).
    """
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME if database else None,
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=True
    )
    return conn

def init_db():
    """
    Initializes the database schema if not already present.
    Executes schema.sql statements.
    """
    # 1. Connect without db to ensure database exists
    conn = get_db_connection(database=False)
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    finally:
        conn.close()

    # 2. Connect to the database and run schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split commands cleanly by semicolon, skipping comments and delimiters
        commands = [cmd.strip() for cmd in sql_content.split(";") if cmd.strip()]
        
        conn = get_db_connection(database=True)
        try:
            with conn.cursor() as cursor:
                for cmd in commands:
                    # Ignore USE database command as connection is already bound
                    if cmd.upper().startswith("USE "):
                        continue
                    if cmd:
                        cursor.execute(cmd)
        finally:
            conn.close()

def query_db(query, args=(), one=False):
    """
    Executes a SELECT query and returns list of dictionaries or single dict.
    """
    conn = get_db_connection(database=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()

def execute_db(query, args=(), return_last_id=False):
    """
    Executes an INSERT, UPDATE, or DELETE statement.
    """
    conn = get_db_connection(database=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            if return_last_id:
                return cursor.lastrowid
            return cursor.rowcount
    finally:
        conn.close()

def execute_many_db(query, seq_of_args):
    """
    Executes an executemany statement for bulk insertions.
    """
    conn = get_db_connection(database=True)
    try:
        with conn.cursor() as cursor:
            cursor.executemany(query, seq_of_args)
            return cursor.rowcount
    finally:
        conn.close()
