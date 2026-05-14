import os
import sqlite3
from config import db_config


def get_connection():
    conn = sqlite3.connect(db_config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database by executing the schema.sql file."""
    conn = get_connection()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
