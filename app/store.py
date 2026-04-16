from app.db import get_db

def store_all(raw_data: dict, fetch_date: str, fetch_time: str):
    with get_db() as conn:
        for day in raw_data.get("weatherForecast", []):
            conn.execute("""
                INSERT OR IGNORE INTO forecasts (
                    fetch_date, fetch_time, forecast_date, week,
                    maxtemp_value, maxtemp_unit, mintemp_value, mintemp_unit,
                    weather, wind, maxrh_value, minrh_value, icon, psr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fetch_date,
                fetch_time,
                day.get("forecastDate"),
                day.get("week"),
                day.get("forecastMaxtemp", {}).get("value"),
                day.get("forecastMaxtemp", {}).get("unit", "C"),
                day.get("forecastMintemp", {}).get("value"),
                day.get("forecastMintemp", {}).get("unit", "C"),
                day.get("forecastWeather"),
                day.get("forecastWind"),
                day.get("forecastMaxrh", {}).get("value"),
                day.get("forecastMinrh", {}).get("value"),
                day.get("ForecastIcon"),
                day.get("PSR"),
            ))
        conn.commit()