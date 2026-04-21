import os
import ssl
from contextlib import contextmanager
from dotenv import load_dotenv
import certifi
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").split("?")[0]

Base = declarative_base()

_sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SyncSessionLocal = sessionmaker(bind=_sync_engine, expire_on_commit=False)

_async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    connect_args={"ssl": ssl.create_default_context(cafile=certifi.where())},
)
AsyncSessionLocal = async_sessionmaker(bind=_async_engine, class_=AsyncSession, expire_on_commit=False)

@contextmanager
def get_db():
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()

def init_db():
    with _sync_engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id SERIAL PRIMARY KEY,
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
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_forecast_date ON forecasts(forecast_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fetch_date ON forecasts(fetch_date)"))
        conn.commit()

# Async versions for API
async def get_db_async():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db_async():
    async with _async_engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id SERIAL PRIMARY KEY,
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
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_forecast_date ON forecasts(forecast_date)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fetch_date ON forecasts(fetch_date)"))
