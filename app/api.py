from datetime import datetime
from fastapi import FastAPI, HTTPException
from app.db import get_db, init_db
from app.models import ForecastRow, Temp, ForecastListResponse

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/forecasts", response_model=ForecastListResponse)
def get_forecasts(date: str | None = None, fetch_date: str | None = None):
    if not date and not fetch_date:
        raise HTTPException(400, "Must provide date or fetch_date query param")

    with get_db() as conn:
        if date:
            rows = conn.execute(
                "SELECT * FROM forecasts WHERE forecast_date = ? ORDER BY fetch_date DESC",
                (date,)
            ).fetchall()
        elif fetch_date:
            rows = conn.execute(
                "SELECT * FROM forecasts WHERE fetch_date = ? ORDER BY forecast_date",
                (fetch_date,)
            ).fetchall()

    forecasts = [_row_to_forecast(r) for r in rows]
    return ForecastListResponse(count=len(forecasts), forecasts=forecasts)

@app.get("/forecasts/latest", response_model=ForecastListResponse)
def get_latest():
    with get_db() as conn:
        latest = conn.execute(
            "SELECT fetch_date FROM forecasts ORDER BY fetch_date DESC LIMIT 1"
        ).fetchone()
        if not latest:
            return ForecastListResponse(count=0, forecasts=[])
        rows = conn.execute(
            "SELECT * FROM forecasts WHERE fetch_date = ? ORDER BY forecast_date",
            (latest["fetch_date"],)
        ).fetchall()
    forecasts = [_row_to_forecast(r) for r in rows]
    return ForecastListResponse(count=len(forecasts), forecasts=forecasts)

@app.get("/forecasts/today", response_model=ForecastListResponse)
def get_today():
    today = datetime.now().strftime("%Y%m%d")
    with get_db() as conn:
        latest = conn.execute(
            "SELECT fetch_date FROM forecasts ORDER BY fetch_date DESC LIMIT 1"
        ).fetchone()
        if not latest:
            return ForecastListResponse(count=0, forecasts=[])
        rows = conn.execute(
            "SELECT * FROM forecasts WHERE forecast_date = ? AND fetch_date = ?",
            (today, latest["fetch_date"])
        ).fetchall()
    forecasts = [_row_to_forecast(r) for r in rows]
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