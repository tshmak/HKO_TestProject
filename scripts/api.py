from datetime import datetime
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.db import get_db_async, init_db_async
from app.models import ForecastRow, Temp, ForecastListResponse

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db_async()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/forecasts", response_model=ForecastListResponse)
async def get_forecasts(date: str | None = None, fetch_date: str | None = None):
    if not date and not fetch_date:
        raise HTTPException(400, "Must provide date or fetch_date query param")

    async for session in get_db_async():
        if date:
            result = await session.execute(
                text("SELECT * FROM forecasts WHERE forecast_date = :date ORDER BY fetch_date DESC"),
                {"date": date}
            )
        elif fetch_date:
            result = await session.execute(
                text("SELECT * FROM forecasts WHERE fetch_date = :fd ORDER BY forecast_date"),
                {"fd": fetch_date}
            )
        rows = result.fetchall()
        break

    forecasts = [_row_to_forecast(r._mapping) for r in rows]
    return ForecastListResponse(count=len(forecasts), forecasts=forecasts)

@app.get("/forecasts/latest", response_model=ForecastListResponse)
async def get_latest():
    async for session in get_db_async():
        result = await session.execute(
            text("SELECT fetch_date FROM forecasts ORDER BY fetch_date DESC LIMIT 1")
        )
        latest = result.fetchone()
        if not latest:
            return ForecastListResponse(count=0, forecasts=[])
        result = await session.execute(
            text("SELECT * FROM forecasts WHERE fetch_date = :fd ORDER BY forecast_date"),
            {"fd": latest["fetch_date"]}
        )
        rows = result.fetchall()
        break

    forecasts = [_row_to_forecast(r._mapping) for r in rows]
    return ForecastListResponse(count=len(forecasts), forecasts=forecasts)

@app.get("/forecasts/today", response_model=ForecastListResponse)
async def get_today():
    today = datetime.now().strftime("%Y%m%d")
    async for session in get_db_async():
        result = await session.execute(
            text("SELECT fetch_date FROM forecasts ORDER BY fetch_date DESC LIMIT 1")
        )
        latest = result.fetchone()
        if not latest:
            return ForecastListResponse(count=0, forecasts=[])
        result = await session.execute(
            text("SELECT * FROM forecasts WHERE forecast_date = :td AND fetch_date = :fd"),
            {"td": today, "fd": latest["fetch_date"]}
        )
        rows = result.fetchall()
        break

    forecasts = [_row_to_forecast(r._mapping) for r in rows]
    return ForecastListResponse(count=len(forecasts), forecasts=forecasts)

def _row_to_forecast(row) -> ForecastRow:
    return ForecastRow(
        fetch_date=row["fetch_date"],
        fetch_time=row["fetch_time"],
        forecast_date=row["forecast_date"],
        week=row["week"],
        maxtemp=Temp(value=row["maxtemp_value"], unit=row["maxtemp_unit"]),
        mintemp=Temp(value=row["mintemp_value"], unit=row["mintemp_unit"]),
        weather=row["weather"],
        wind=row["wind"],
        maxrh=Temp(value=row["maxrh_value"], unit="percent") if row["maxrh_value"] else None,
        minrh=Temp(value=row["minrh_value"], unit="percent") if row["minrh_value"] else None,
        icon=row["icon"],
        psr=row["psr"],
    )