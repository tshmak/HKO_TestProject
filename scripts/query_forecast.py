#!/usr/bin/env python3
import argparse
import json
from sqlalchemy import text
from app.db import get_db

def list_forecasts(limit=10):
    with get_db() as conn:
        result = conn.execute(
            text("""
                SELECT fetch_date, forecast_date, week, maxtemp_value, mintemp_value,
                       weather, wind, psr
                FROM forecasts
                ORDER BY fetch_date DESC, forecast_date ASC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        return [dict(r._mapping) for r in result.fetchall()]

def query_by_date(forecast_date):
    with get_db() as conn:
        result = conn.execute(
            text("SELECT * FROM forecasts WHERE forecast_date = :fd"),
            {"fd": forecast_date}
        )
        return [dict(r._mapping) for r in result.fetchall()]

def main(args):
    if args.date:
        results = query_by_date(args.date)
    else:
        results = list_forecasts(args.limit)
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Query HKO forecast database")
    p.add_argument("-d", "--date", help="Forecast date (YYYYMMDD)")
    p.add_argument("-l", "--limit", type=int, default=10, help="Number of forecasts to list")
    args = p.parse_args()
    main(args)
