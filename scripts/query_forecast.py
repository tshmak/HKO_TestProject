#!/usr/bin/env python3
import argparse
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "hko.db"


def list_forecasts(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT fetch_date, forecast_date, week, maxtemp_value, mintemp_value, weather, wind, psr "
        "FROM forecasts ORDER BY fetch_date DESC, forecast_date ASC LIMIT ?",
        (limit,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def query_by_date(forecast_date):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT * FROM forecasts WHERE forecast_date = ?",
        (forecast_date,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


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
