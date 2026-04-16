import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "hko.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fetch_date TEXT NOT NULL,
                fetch_time TEXT NOT NULL,
                forecast_date TEXT NOT NULL,
                week TEXT NOT NULL,
                maxtemp_value INTEGER NOT NULL,
                maxtemp_unit TEXT NOT NULL DEFAULT 'C',
                mintemp_value INTEGER NOT NULL,
                mintemp_unit TEXT NOT NULL DEFAULT 'C',
                weather TEXT,
                wind TEXT,
                maxrh_value INTEGER,
                minrh_value INTEGER,
                icon INTEGER,
                psr TEXT,
                UNIQUE(forecast_date, fetch_date)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_forecast_date ON forecasts(forecast_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fetch_date ON forecasts(fetch_date)")
        conn.commit()